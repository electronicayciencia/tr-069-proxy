#include <stdio.h>

int gsdfDecryptFile(char *src_file, char *dst_file);
int gsdfEncryptFile(char *src_file, char *tag, char *dst_file);
char *tag = "default";

int main(int argc, char *argv[]) {
  int i = 0;

  if(argc != 4 || (argv[1][0] != 'e' && argv[1][0] != 'd')) {
    printf("Usage: %s [e|d] file_in file_out\n", argv[0]);
    return -1;
  }

  switch(argv[1][0]) {
    case 'e':
      i = gsdfEncryptFile(argv[2], tag, argv[3]);
      printf("Encryption returned: %d\n", i);
      break;
    case 'd':
      i = gsdfDecryptFile(argv[2], argv[3]);
      printf("Decryption returned: %d\n", i);
      break;
  }
  return 0;
}

