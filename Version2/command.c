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

	FILE *opfile,*cdbfile,*resfile;
	
  	char *inname = "Simulatordata/opcode.txt";
	char name[50];
	char opcode[10];
 	char cdb[20];
	char res[20];
 	char line[100];
	char linec[100];
	char cmd[16][30];
	int n,j,k=0,l;
  	int i = 0;


  	opfile = fopen(inname, "r");
	printf("---------\n");
	
  	if (!opfile) {
    		printf("Couldn't open %s for reading\n",inname);
    	return -1;
  	}
	while(i < 40 && fgets(line, sizeof(line), opfile) != NULL){
        	sscanf(line, "%s\t%s\t%s", opcode,cdb,res);
		n = (int)strtol(opcode, NULL, 0);
		printf("%d  %d\n",n,io_hdr->cmdp[0]);
		if(n==(io_hdr->cmdp[0])){
			strcpy(name,"Simulatordata/cdb/");
			strcat(name,cdb);
			strcat(name,".txt");
			
			cdbfile = fopen(name, "r");
				
  			if (!cdbfile) {
    				printf("Couldn't open %s for reading\n",cdb);
    				return -1;
  			}
			while(fgets(linec, sizeof(linec), cdbfile) != NULL){
				for (i = 0,j=0; i < sizeof(linec); i++) 
				{ 
							
					if (linec[i] == '\t') {
						cmd[k][j] = '\0';
						j=0;
						k++;
						
							
					} 
					else { cmd[k][j] = linec[i];
						j++; 
						 } 
				}
				printf("\n");
				for(l=0;l<k;l++)
					printf("%s ",cmd[l]);
				k=0;
				
		}
		}
		
		else{
			printf("Invalid opcode\n");
		
		}
        	i++;
    	}
				
	return 0;
}






