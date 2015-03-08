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
     _fields_ = [("interface_id",c_int),
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


inqCmdBlk = (c_ubyte *INQ_CMD_LEN)(INQ_CMD_CODE, 0, 0, 0, INQ_REPLY_LEN, 0)

inqBuff = (c_ubyte * INQ_REPLY_LEN)()

sense_buffer = (c_ubyte * 32)()


io_hdr=SgIoHdr(interface_id=ord('S'),
               dxfer_direction = SG_DXFER_FROM_DEV,
               cmd_len = sizeof(inqCmdBlk),
	       iovec_count = 0,
    	       mx_sb_len = sizeof(sense_buffer),
    	       dxfer_len = INQ_REPLY_LEN,
               cmdp = cast(inqCmdBlk, c_void_p),
	       dxferp = cast(inqBuff, c_void_p),
	       sbp = cast(sense_buffer, c_void_p),
    	       timeout = 20000)  

libinquiry = cdll.LoadLibrary('./libinquiry.so.1.0')

sg_inquiry=libinquiry.sg_inquiry
sg_inquiry.argtypes = (POINTER(SgIoHdr),)
sg_inquiry.restype = c_int

ret=sg_inquiry(byref(io_hdr))

print "-----------------------------"
print "python output"
print "Some of the INQUIRY command's response: "

t=cast(io_hdr.dxferp,POINTER(c_char))

l=["PQual","Device_type","RMB","version","NormACA","HiSUP","Resp_data_format","SCCS","ACC","TPGS","3PC", "Protect","[BQue]","EncServ","MultiP","[MChngr]","[ACKREQQ]","Addr16","[RelAdr]","WBus16","Sync",  "Linked","[TranDis]","CmdQue","length","Peripheral device type","Vendor identification","Product identification","Product revision level"]


def ptr_addr(ptr,offset):
	x=addressof(ptr.contents)+offset
	return pointer(type(ptr.contents).from_address(x))
	
m=ptr_addr(t,0)
st=m.contents.value
r=bin(ord(st))[2:].zfill(8) 
print l[0],"=",r[5:],l[1],"=",r[0:5],

m=ptr_addr(t,1)
st=m.contents.value
r=bin(ord(st))[2:].zfill(8) 
print l[2],"=",r[7:]

m=ptr_addr(t,2)
st=m.contents.value 
print l[3],"=",hex(ord(st))






for i in range(0,7):
	x=addressof(t.contents)+i
	m=pointer(type(t.contents).from_address(x))
	st=m.contents.value
	r=bin(ord(st))[2:].zfill(8) 
	print r,st,x,

for i in range(8,15):
	x=addressof(t.contents)+i
	m=pointer(type(t.contents).from_address(x))
	print m.contents.value,

x=addressof(t.contents)+8
m=pointer(type(t.contents).from_address(x))
print m.contents.value,


for i in range(16,31):
	x=addressof(t.contents)+i
	m=pointer(type(t.contents).from_address(x))
	print m.contents.value,



for i in range(32,35):
	x=addressof(t.contents)+i
	m=pointer(type(t.contents).from_address(x))
	print m.contents.value,


print "INQUIRY Duration=",io_hdr.duration,"millisecs"
print "resid=",io_hdr.resid





