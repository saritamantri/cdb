from ctypes import *
"""
typedef struct sg_io_hdr
{
    int interface_id;           /* [i] 'S' for SCSI generic (required) */
    int dxfer_direction;        /* [i] data transfer direction  */
    unsigned char cmd_len;      /* [i] SCSI command length ( <= 16 bytes) */
    unsigned char mx_sb_len;    /* [i] max length to write to sbp */
    unsigned short iovec_count; /* [i] 0 implies no scatter gather */
    unsigned int dxfer_len;     /* [i] byte count of data transfer */
    void * dxferp;              /* [i] [*io] points to data transfer memory or
                                             scatter gather list */
    unsigned char * cmdp;       /* [i] [*i] points to SCSI command to perform */
    unsigned char * sbp;        /* [i] [*o] points to sense_buffer memory */
    unsigned int timeout;       /* [i] MAX_UINT->no timeout (unit: millisec) */
    unsigned int flags;         /* [i] 0 -> default, see SG_FLAG... */
    int pack_id;                /* [i->o] unused internally (normally) */
    void * usr_ptr;             /* [i->o] unused internally */
    unsigned char status;       /* [o] scsi status */
    unsigned char masked_status;/* [o] shifted, masked scsi status */
    unsigned char msg_status;   /* [o] messaging level data (optional) */
    unsigned char sb_len_wr;    /* [o] byte count actually written to sbp */
    unsigned short host_status; /* [o] errors from host adapter */
    unsigned short driver_status;/* [o] errors from software driver */
    int resid;                  /* [o] dxfer_len - actual_transferred */
    unsigned int duration;      /* [o] time taken (unit: millisec) */
    unsigned int info;          /* [o] auxiliary information */
} sg_io_hdr_t;  /* around 64 bytes long (on i386) */
"""
INQ_REPLY_LEN = 96
INQ_CMD_CODE = 0x12
INQ_CMD_LEN = 6
SG_DXFER_NONE=-1
SG_DXFER_TO_DEV=-2
SG_DXFER_FROM_DEV=-3
SG_DXFER_TO_FROM_DEV=-4

import pdb

class SgIoHdr(Structure):
     _fields_ =[("interface_id",c_int),
            	("dxfer_direction",c_int),
	    	("cmd_len",c_ubyte),
           	("mx_sb_len",c_ubyte),
		("iovec_count", c_ushort),
		("dxfer_len", c_uint),
                ("dxferp",c_void_p),
		("cmdp",c_void_p),
		("sbp",c_void_p),
		("timeout",c_uint),
		("flags", c_uint),
		("pack_id", c_int),
		("usr_ptr", c_void_p),
		("status", c_ubyte),
		("masked_status", c_ubyte),
		("msg_status", c_ubyte),
		("sb_len_wr",c_ubyte ),	
		("host_status",c_ushort ),
		("driver_status", c_ushort),
		("resid",c_int ),
		("duration",c_uint ),
		("info",c_uint)]

class CDB:

	def __init__(self,opcode,CMDDT,EVDT,pagecode,reply_len,control,dxfer,count,to):
		self.inqCmdBlk = (c_ubyte *INQ_CMD_LEN)(opcode, 0, 0, 0, reply_len, 0)
		self.inqBuff = (c_ubyte * reply_len)()
		self.sense_buffer = (c_ubyte * 32)()

		self.io_hdr= SgIoHdr(interface_id=ord('S'),
				     dxfer_direction = dxfer,
				     cmd_len = sizeof(self.inqCmdBlk),
				     iovec_count = count,
				     mx_sb_len = sizeof(self.sense_buffer),
				     dxfer_len = reply_len,
				     cmdp = cast(self.inqCmdBlk, c_void_p),
				     dxferp = cast(self.inqBuff, c_void_p),
                                     sbp = cast(self.sense_buffer, c_void_p),
                                     timeout =to)  


	def loadlib(self,lib):
		self.libinquiry = cdll.LoadLibrary(lib)
		self.sg_inquiry=self.libinquiry.sg_inquiry
		self.sg_inquiry.argtypes = (POINTER(SgIoHdr),)
		self.sg_inquiry.restype = c_int


	def call(self):
		self.ret=self.sg_inquiry(byref(self.io_hdr))
		return self.ret

		

'''l=["PQual","Device_type","RMB","version","NormACA","HiSUP","Resp_data_format","SCCS","ACC","TPGS","3PC", "Protect","[BQue]","EncServ","MultiP","[MChngr]","[ACKREQQ]","Addr16","[RelAdr]","WBus16","Sync",  "Linked","[TranDis]","CmdQue","length","Peripheral device type","Vendor identification","Product identification","Product revision level"]'''


class Response:
	
	def __init__(self,dataformat):
		self.dataformat=dataformat

	def ptr_addr(self,ptr,offset):
		x=addressof(ptr.contents)+offset
		return pointer(type(ptr.contents).from_address(x))
	
	def getResponse(self,ptr,field):
		if self.dataformat[field][4]=='b':
			m=self.ptr_addr(ptr,self.dataformat[field][1])
			st=m.contents.value
			r=bin(ord(st))[2:].zfill(8)
			return r[self.dataformat[field][2]:self.dataformat[field][3]+1] 

		elif self.dataformat[field][4]=='h':
			m=self.ptr_addr(ptr,self.dataformat[field][1])
			st=m.contents.value
			r=hex(ord(st))
			return r 
		else:
			r=""
			for i in range(0,self.dataformat[field][0]):
				m=self.ptr_addr(ptr,self.dataformat[field][1]+i)
				r=r+m.contents.value
			return r


'''print res.getResponse(t,"Device_type")
print res.getResponse(t,"RMB")
print res.getResponse(t,"Version")
print res.getResponse(t,"Vendor_identification")
print res.getResponse(t,"Product_identification")
print res.getResponse(t,"Product_revision_level")'''







