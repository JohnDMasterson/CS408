CC = gcc
CFLAGS = -g -O2
LINKER = -lusb-1.0
OBJECTS = iclicker.o

iclicker.exe : $(OBJECTS)
	$(CC) $(CFLAGS) $(OBJECTS) $(LINKER) -o iclicker

%.o : %.c
	$(CC) $(CFLAGS) -c $<

clean :
	rm $(OBJECTS) iclicker

tidy :
	rm $(OBJECTS)
