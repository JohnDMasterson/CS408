#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <time.h>

#include "libusb.h"
int shouldRead = 1;
void printUSBPacket(unsigned char* data, int length)
{
  int i;
  printf("bytes transfered: %d\n", length);
  printf("data: ");
  for(i=0; i<length; i++)
  {
    if(i%16 == 0){printf("\n");}
    if(i%8 == 0){printf("\t");}
    printf("%02X ", data[i]);
  }
  printf("\n\n");
}

unsigned char* padIClickerBaseCommand(char* unpadded, int length)
{
  if(length < 0 || length > 64)
  {
    return NULL;
  }
  // allocated memory for command
  unsigned char * ret = (unsigned char*)malloc(64*sizeof(char));
  int i;
  //copies original command over to the new command
  for(i=0; i<length; i++) {
    ret[i] = unpadded[i];
  }
  //pads it to 64 bytes
  for(i=i; i<64; i++) {
    ret[i] = 0x0;
  }
  return ret;
}

//enum for poll types
typedef enum {ALPHA, NUMERIC, ALPHANUMERIC} iPollType;

typedef struct
{
  // libusb session
  libusb_context *ctx;
  // handle for base
  libusb_device_handle *base;
  // frequency for iClickerBase
  char frequency[2];
  // initialized
  int initialized;
  // is there a poll going on
  int isPolling;
} iClickerBase;

iClickerBase* getIClickerBase()
{
  iClickerBase* iBase = (iClickerBase*)malloc(sizeof(iClickerBase));
  iBase->initialized = 0;
  iBase->isPolling = 0;
  iBase->ctx = NULL;
  iBase->base = NULL;
  int rc = libusb_init (&iBase->ctx);
  if (rc < 0)
  {
    return iBase;
  }
  // sets to recommended debug level
  libusb_set_debug(iBase->ctx, 3);

  int VENDOR_ID = 0x1881;
  int PRODUCT_ID = 0x0150;
  iBase->base = libusb_open_device_with_vid_pid(iBase->ctx, VENDOR_ID, PRODUCT_ID); //these are vendorID and productID I found for my usb device
  if(iBase->base != NULL)
  {

      int iface, nb_ifaces;
      struct libusb_config_descriptor *conf_desc;
      struct libusb_device *dev;
      dev = libusb_get_device(iBase->base);
      libusb_get_config_descriptor(dev, 0, &conf_desc);
      nb_ifaces = conf_desc->bNumInterfaces;
      printf("(bus %d, device %d)",
		    libusb_get_bus_number(dev), libusb_get_device_address(dev));
      printf("Number of interfaces: %d\n", nb_ifaces);

    //find out if kernel driver is attached
    if(libusb_kernel_driver_active(iBase->base, 0) == 1) {
      printf("Kernel driver already active\n");
      //detach it
      if(libusb_detach_kernel_driver(iBase->base, 0) == 0)
      {
        printf("Kernel driver detached\n");
      }
      else
      {
        printf("Kernel driver NOT detached\n");
      }
    }
    else
    {
      printf("Kernel driver NOT already active\n");
    }


    //libusb_release_interface(iBase->base, 0);
    rc = libusb_claim_interface(iBase->base, 0);
  }


  return iBase;
}


void displayIClickerBaseInterruptIn(iClickerBase* iBase)
{
  unsigned char* data = (unsigned char*)malloc(64*sizeof(char));
  int i;
  for(i = 0; i<64; i++){data[i] = 0;}
  int len;
  int tries = libusb_interrupt_transfer(iBase->base, 0x83, data, 64, &len, 1000);
  //if(tries) 
  printUSBPacket(data, len);
  free(data);
}

void sendIClickerBaseControlTransfer(iClickerBase *iBase, char* commandstring, int length)
{
  if(iBase->initialized)
  {
    // pads the command string
    unsigned char* paddedcommand = padIClickerBaseCommand(commandstring, length);
    // sends the command to the base
    libusb_control_transfer(iBase->base,0x21,0x09,0x0200,0x0000,paddedcommand,64,1000);
    free(paddedcommand);
    if(shouldRead)
      displayIClickerBaseInterruptIn(iBase);
  }
}

void setIClickerBaseDisplay(iClickerBase *iBase, char* displayString, int length, int line)
{
  if(iBase->initialized)
  {
    // check if the length is between 0 and 16
    if(length < 0 || length > 16) {
      return;
    }
    // check if line number is valid
    if(line < 0 || line > 1) {
      return;
    }
    char* command = (char*)malloc(18*sizeof(char));
    command[0] = 0x01;
    command[1] = 0x13 + line;
    int i;
    for(i=0; i<length; i++)
    {
      command[2+i] = displayString[i];
    }
    for(i=i; i<16; i++)
    {
      command[2+i] = 0x20;
    }
    shouldRead = 0;
    sendIClickerBaseControlTransfer(iBase, command, 18);
    free(command);
    shouldRead = 1;
  }
}

void setIClickerBaseFrequency(iClickerBase* iBase, char first, char second)
{
  if(iBase->base != NULL && !iBase->isPolling)
  {
    if(first < 'a' || first > 'd' || second < 'a' || second > 'd')
    {
      return;
    }
    iBase->frequency[0] = first;
    iBase->frequency[1] = second;
    char* command = (char*)malloc(4*sizeof(char));
    command[0] = 0x01;
    command[1] = 0x10;
    command[2] = 0x21 + first - 'a';
    command[3] = 0x41 + second - 'a';
    sendIClickerBaseControlTransfer(iBase, command, 4);
    command[1] = 0x16;
    sendIClickerBaseControlTransfer(iBase, command, 2);
    free(command);
  }
}

void setIClickerBaseVersion2(iClickerBase* iBase)
{
  if(iBase->base != NULL && !iBase->isPolling)
  {
  char* command = (char*)malloc(2*sizeof(char));
  command[0] = 0x01;
  command[1] = 0x2d;
  sendIClickerBaseControlTransfer(iBase, command, 2);
  free(command);
  }
}

void setIClicketBasePollType(iClickerBase* iBase, iPollType type)
{
  if(iBase->base != NULL && !iBase->isPolling)
  {
  char* command = (char*)malloc(5*sizeof(char));
  command[0] = 0x01;
  command[1] = 0x19;
  command[2] = 0x66 + type;
  command[3] = 0x00;
  command[4] = 0x00;
  sendIClickerBaseControlTransfer(iBase, command, 5);
  free(command);
  }
}

void initIClickerBase(iClickerBase* iBase)
{
  if(!iBase->initialized)
  {
    setIClickerBaseFrequency(iBase, 'a', 'a');

    char* command = (char*)malloc(9*sizeof(char));
    command[0] = 0x01;
    command[1] = 0x2a;
    command[2] = 0x21;
    command[3] = 0x41;
    command[4] = 0x05;
    sendIClickerBaseControlTransfer(iBase, command, 5);
    command[1] = 0x12;
    sendIClickerBaseControlTransfer(iBase, command, 2);
    command[1] = 0x15;
    sendIClickerBaseControlTransfer(iBase, command, 2);
    command[1] = 0x16;
    sendIClickerBaseControlTransfer(iBase, command, 2);



    setIClickerBaseVersion2(iBase);

    command[1] = 0x29;
    command[2] = 0xa1;
    command[3] = 0x8f;
    command[4] = 0x96;
    command[5] = 0x8d;
    command[6] = 0x99;
    command[7] = 0x97;
    command[8] = 0x8f;
    sendIClickerBaseControlTransfer(iBase, command, 9);
    command[1] = 0x17;
    command[2] = 0x04;
    sendIClickerBaseControlTransfer(iBase, command, 3);
    command[1] = 0x17;
    command[2] = 0x03;
    sendIClickerBaseControlTransfer(iBase, command, 3);
    command[1] = 0x16;
    sendIClickerBaseControlTransfer(iBase, command, 2);


    iBase->initialized = 1;
  }
}

void startIClickerBasePoll(iClickerBase* iBase)
{
  if(iBase->initialized && !iBase->isPolling)
  {
    char* command = (char*)malloc(3*sizeof(char));
    command[0] = 0x01;
    command[1] = 0x17;
    command[2] = 0x03;
    sendIClickerBaseControlTransfer(iBase, command, 3);
    command[1] = 0x17;
    command[2] = 0x05;
    sendIClickerBaseControlTransfer(iBase, command, 3);
    setIClicketBasePollType(iBase, 0);
    command[1] = 0x11;
    sendIClickerBaseControlTransfer(iBase, command, 2);
  }
}

void stopIClickerBasePoll(iClickerBase* iBase)
{
  if(iBase->initialized && iBase->isPolling)
  {
    char* command = (char*)malloc(3*sizeof(char));
    command[0] = 0x01;
    command[1] = 0x12;
    sendIClickerBaseControlTransfer(iBase, command, 2);
    command[1] = 0x16;
    sendIClickerBaseControlTransfer(iBase, command, 2);
    command[1] = 0x17;
    command[2] = 0x01;
    sendIClickerBaseControlTransfer(iBase, command, 3);
    command[1] = 0x17;
    command[2] = 0x03;
    sendIClickerBaseControlTransfer(iBase, command, 3);
    command[1] = 0x17;
    command[2] = 0x04;
    sendIClickerBaseControlTransfer(iBase, command, 3);
  }
}

void closeIClickerBase(iClickerBase* iBase)
{
  if(iBase->initialized)
  {
    if(iBase->isPolling)
    {
      stopIClickerBasePoll(iBase);
    }
    if(iBase->base != NULL)
    {
      libusb_close(iBase->base); //close the device we opened
    }
    if(iBase->ctx != NULL)
    {
      libusb_exit(iBase->ctx); //needs to be called to end
    }
  }
}

void displayIClickerBaseResponse(iClickerBase* iBase)
{
  unsigned char* data = (unsigned char*)malloc(64*sizeof(char));
  int i;
  for(i = 0; i<64; i++){data[i] = 0;}
  int len = 0;
  int ret = 0;
  int tries = 0;
  while ( len <= 0 || ret < 0){
    ret = libusb_interrupt_transfer(iBase->base, 0x83, data, 64, &len, 1000);
    printf("%d\n",ret);
    printUSBPacket(data, len);
  };
  //printUSBPacket(data, len);
  free(data);
}

typedef struct
{
  //iClicker user Id
  int id;
  //latest response
  char lastResponse;
  //time of the close
  time_t lastClicked;
} iClickerResponse;

typedef struct
{
  // base associated with the poll
  iClickerBase* iBase;
  // is a poll running
  int isPolling;
  // poll type
  iPollType type;

} iClickerPoll;

iClickerPoll* createIClickerPoll()
{
  iClickerPoll *iPoll = (iClickerPoll*)malloc(sizeof(iClickerPoll));
  return iPoll;
}

void setIClickerPollType(iClickerPoll* iPoll, iPollType type)
{
  iPoll->type = type;
  setIClicketBasePollType(iPoll->iBase, type);
}

void closeIClickerPoll(iClickerPoll* iPoll)
{
  free(iPoll);
}

int main()
{
  iClickerBase* iBase = getIClickerBase();

  initIClickerBase(iBase);
  setIClickerBaseFrequency(iBase, 'c', 'd');
  //displayIClickerBaseInterruptIn(iBase);

  //setIClickerBaseDisplay(iBase, "Now Polling", 11, 0);
  //displayIClickerBaseInterruptIn(iBase);
  //setIClickerBaseDisplay(iBase, "  ", 2, 1);
  startIClickerBasePoll(iBase);
  displayIClickerBaseResponse(iBase);
  stopIClickerBasePoll(iBase);
  setIClickerBaseDisplay(iBase, "Polling ended", 13, 0);
  closeIClickerBase(iBase);
  return 0;
}
