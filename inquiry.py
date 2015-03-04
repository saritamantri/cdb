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
sg_inquiry.restype = POINTER(SgIoHdr)

sg_inquiry(byref(io_hdr))

print "-----------------------------"
print "python output"
print "Some of the INQUIRY command's response: "

t=cast(io_hdr.dxferp,POINTER(c_char))

for i in range(8,32):
	x=addressof(t.contents)+i
	m=pointer(type(t.contents).from_address(x))
	print m.contents.value,

print "INQUIRY Duration=",io_hdr.duration,"millisecs"
print "resid=",io_hdr.resid





