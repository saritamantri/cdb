#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <scsi/sg.h> 
int user_ioctl(int , int ,sg_io_hdr_t* io_hdr);

int sg_inquiry(sg_io_hdr_t* io_hdr,char *indata,char *outdata,int len)
    {
	
	int sg_fd, k,status,res,val;
	char *sd;
	io_hdr->dxferp=indata;
	
	if ((sg_fd = open("/dev/sg2", O_RDONLY)) < 0) {
    	/* Note that most SCSI commands require the O_RDWR flag to be set */
        perror("error opening given file name");
        return 1;
	    }
	    /* It is prudent to check we have a sg device by trying an ioctl */
	if ((ioctl(sg_fd, SG_GET_VERSION_NUM, &k) < 0) || (k < 30000)) {
        printf("Not an sg device, or old sg driver\n");
        return 1;
	    }


 	if (val=user_ioctl(sg_fd, SG_IO,io_hdr) < 0) {
        perror("SG_IO ioctl error");
        return 1;
    }

        
    /* now for the error processing */
    if ((io_hdr->info & SG_INFO_OK_MASK) != SG_INFO_OK) {
        if (io_hdr->sb_len_wr > 0) {
            printf("sense data: ");
	    sd=(char *)(io_hdr->sbp);
	    printf("byte count %d\n",io_hdr->sb_len_wr);
            for (k = 0; k < io_hdr->sb_len_wr; ++k) {
                if ((k > 0) && (0 == (k % 10)))
                    printf("\n  ");
                  printf("0x%02x ", sd[k]);
	
				    
            }
            printf("\n");
	    
        }
        if (io_hdr->masked_status)
            printf("SCSI status=0x%x\n", io_hdr->status);
        if (io_hdr->host_status)
            printf("host_status=0x%x\n", io_hdr->host_status);
        if (io_hdr->driver_status)
            printf("driver_status=0x%x\n", io_hdr->driver_status);
    }
    else {  /* assume INQUIRY response is present */
       /*char * p = (char *)io_hdr->dxferp;
       	strcpy(outdata,p);
       	printf("command's response:\n");
	printf("%s\n",p+8);

      	printf("INQUIRY duration=%u millisecs, resid=%d\n",
               io_hdr->duration, io_hdr->resid);
       	printf("%s-----%s-----%d\n",p,outdata,io_hdr->cmdp[0]);	*/
	printf("commands response\n");
    }
    close(sg_fd);
    return val;
}

int user_ioctl(int sg_fd, int sg_io,sg_io_hdr_t* io_hdr)
{

	char Buff[256];
	printf("command's response:\n");
	switch(io_hdr->cmdp[0])
	{

		case 0x0a: printf("%d\n",io_hdr->cmdp[0]);
			   if(io_hdr->cmdp[1]+io_hdr->cmdp[2]<=2097664)
			   		io_hdr->status=0;
			   else
					io_hdr->status=2;
			   

		default: printf("Invalid opcode\n");
	}
	
	io_hdr->status=0;
				
	
}









