#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <scsi/sg.h> 

int main()
{
  int fd, res;
  const int t_length = 20;             
  //unsigned char rdCmdBlk10[6] ={ 0x08,0, 0, 0, 0, 0 };
  //unsigned char rdCmdBlk10[16]= {0x88, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0};
  unsigned char wrCmdBlk10[10]= {0x2a, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  unsigned char sense_b[36];
  sg_io_hdr_t io_hdr;
  unsigned char data[512]={"hello world"};
  unsigned char rdCmdBlk10[10]= {0x28, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  unsigned char rdata[512];

  // Open device
  
if ((fd = open("/dev/sg2", O_RDONLY)) < 0) {
            perror("file opening error");
            return 1;
        }

  
  // Prepare SCSI READ (6) command
  wrCmdBlk10[1]  = 0x00;
  wrCmdBlk10[2]  = 0x00;           
  wrCmdBlk10[3]  = 0x00;           
  wrCmdBlk10[4]  = 0x00;       
  wrCmdBlk10[5]  = 0x00;
  wrCmdBlk10[6]  = 0x00;
  wrCmdBlk10[7]  = 0x00;
  wrCmdBlk10[8]  = 0x00;
  wrCmdBlk10[9]  = t_length; 
  // Prepare the sg_io_hdr_t structure
  memset(&io_hdr, 0, sizeof(sg_io_hdr_t));
  io_hdr.interface_id = 'S';                  // Always set to 'S' for sg driver
  io_hdr.cmd_len = sizeof(wrCmdBlk10);         // Size of SCSI command
  io_hdr.mx_sb_len  = sizeof(sense_b);        // Max sense buffer size(for error)
  io_hdr.dxfer_direction = SG_DXFER_TO_DEV; // Data transfer direction(no data)
  io_hdr.dxfer_len = t_length;                // Data transfer length(512)
  io_hdr.dxferp = data;                       // Data transfer buffer(none)
  io_hdr.cmdp = wrCmdBlk10;                    // SCSI command buffer
  io_hdr.sbp = sense_b;                       // Sense buffer
  io_hdr.timeout = 5000;                      // Timeout(5s)
 
  // Sends the command to device
  if ((res = ioctl(fd, SG_IO, &io_hdr)) < 0) {
    close(fd);
     printf("error1\n");
	perror("SG_IO ioctl error");
    return -1;
  }
 
  // Error processing
  if ( ((io_hdr.info & SG_INFO_OK_MASK) != SG_INFO_OK) || // check info
       (io_hdr.masked_status != 0x00) ||                  // check status(0 if ioctl success)
       (io_hdr.msg_status != 0x00) ||                     // check message status
       (io_hdr.host_status != 0x00) ||                    // check host status
       (io_hdr.driver_status != 0x00) )                   // check driver status
  {
    close(fd);
    printf("error 2 \n");
    return -1;
  } else
  {
    close(fd);
    printf("The data is: %s\n",data);
    
  }

if ((fd = open("/dev/sg2", O_RDONLY)) < 0) {
            perror("file opening error");
            return 1;
        }

  
  rdCmdBlk10[1]  = 0x00;           
  rdCmdBlk10[2]  = 0x00;           
  rdCmdBlk10[3]  = 0x00;
  rdCmdBlk10[4]  = 0x00;
  rdCmdBlk10[5]  = 0x00;
  rdCmdBlk10[6]  = 0x00;
  rdCmdBlk10[7]  = 0x00;        
  rdCmdBlk10[8]  = 0x00;       
  rdCmdBlk10[9]  = t_length;


memset(&io_hdr, 0, sizeof(sg_io_hdr_t));
  io_hdr.interface_id = 'S';                  // Always set to 'S' for sg driver
  io_hdr.cmd_len = sizeof(rdCmdBlk10);         // Size of SCSI command
  io_hdr.mx_sb_len  = sizeof(sense_b);        // Max sense buffer size(for error)
  io_hdr.dxfer_direction = SG_DXFER_FROM_DEV; // Data transfer direction(no data)
  io_hdr.dxfer_len = t_length;                // Data transfer length(512)
  io_hdr.dxferp = rdata;                       // Data transfer buffer(none)
  io_hdr.cmdp = rdCmdBlk10;                    // SCSI command buffer
  io_hdr.sbp = sense_b;                       // Sense buffer
  io_hdr.timeout = 5000;                      // Timeout(5s)
 
  // Sends the command to device
  if ((res = ioctl(fd, SG_IO, &io_hdr)) < 0) {
    close(fd);
     printf("error1\n");
	perror("SG_IO ioctl error");
    return -1;
  }
 
  // Error processing
  if ( ((io_hdr.info & SG_INFO_OK_MASK) != SG_INFO_OK) || // check info
       (io_hdr.masked_status != 0x00) ||                  // check status(0 if ioctl success)
       (io_hdr.msg_status != 0x00) ||                     // check message status
       (io_hdr.host_status != 0x00) ||                    // check host status
       (io_hdr.driver_status != 0x00) )                   // check driver status
  {
    close(fd);
    printf("error 2 \n");
    return -1;
  } else
  {
    printf("The data is: %s\n",rdata);
    close(fd);
    
    return 0;
  }



}




