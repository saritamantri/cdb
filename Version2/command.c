#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <scsi/sg.h>
#include <glib.h> 



int user_ioctl(int , int ,sg_io_hdr_t* io_hdr);

int sg_inquiry(sg_io_hdr_t* io_hdr,char *indata,char *outdata,int len)
    {
	printf("...................");
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

void dowrite6(sg_io_hdr_t* io_hdr);
void doinquiry(sg_io_hdr_t* io_hdr);
void doread6(sg_io_hdr_t* io_hdr);

void (*write6)(sg_io_hdr_t* io_hdr)=dowrite6;
void (*inquiry)(sg_io_hdr_t* io_hdr)=doinquiry;
void (*read6)(sg_io_hdr_t* io_hdr)=doread6;


void doinquiry(sg_io_hdr_t *io_hdr)
{
	printf("----inquiry---");
}

void doread6(sg_io_hdr_t *io_hdr)
{
	printf("read6");
}

void dowrite6(sg_io_hdr_t *io_hdr)
{

	/*lba_max=getlbamax()
	lba_min=getlbamin()
	trlen_max=gettrlen()*/
	printf("write");
}

int user_ioctl(int sg_fd, int sg_io,sg_io_hdr_t* io_hdr)
{
char snum[3];
char *key1,*key2,*key3,*op;
void (*value)(sg_io_hdr_t* io_hdr);

GHashTable* ophash = g_hash_table_new(g_direct_hash, g_direct_equal);

key1 = strdup( "10" );
key2 = strdup( "12" );
key3 = strdup( "08" );
g_hash_table_insert(ophash,key1,write6);
g_hash_table_insert(ophash,key2,inquiry);
g_hash_table_insert(ophash,key3,read6);


snprintf (snum, sizeof(snum), "%d",io_hdr->cmdp[0]);
op=strdup(snum);
printf("%s %s",key1,snum);

value=g_hash_table_lookup(ophash, op);
//value(io_hdr);

	return 0;

}






