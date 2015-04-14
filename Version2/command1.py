from ctypes import *
from collections import Counter
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
		
	def __init__(self,**kwargs):
		cdbformat={'0x0a':{'CMD_LEN':6,'REPLY_LEN':512,'DXFER':-2,'format':[('lba',3,1,0,0),('t_length',1,4,0,7),('control',1,5,0,7)],'TR_LEN':1,'timeout':5000},'0x12':{'CMD_LEN':6,'REPLY_LEN':96,'DXFER':-3,'TR_LEN':0,'timeout':20000,'format':[('CMDDT',1,1,1,1),('EVDT',1,1,0,0),('pagecode',1,2,0,7),('alloclen',2,3,0,0),('control',1,5,0,7)]},
		'0x08':{'CMD_LEN':6,'REPLY_LEN':512,'DXFER':-3,'format':[('lba',3,1,0,0),('t_length',1,4,0,7),('control',1,5,0,7)],'TR_LEN':1,'timeout':5000}}
		
		l=cdbformat[kwargs['opcode']]['CMD_LEN']
		r=cdbformat[kwargs['opcode']]['REPLY_LEN']
		dx=cdbformat[kwargs['opcode']]['DXFER']
		self.CmdBlk = (c_ubyte * l)()
		self.CmdBlk[0]=int(kwargs['opcode'],16)
		self.Buff = (c_ubyte * r)()
		self.sense_buffer = (c_ubyte * 32)()	
		self.outdata=create_string_buffer(50)
		self.ptrdata = c_char_p(addressof(self.outdata))
	
		for l in cdbformat[kwargs['opcode']]['format']:
			for k,v in kwargs.items():
				if l[0]==k:
					if l[1]>1 or (l[1]==1 and l[3]==0 and l[4]==7):
						i=l[2]
						self.CmdBlk[i]=v
						
					
					elif l[1]==1 and l[3]==l[4]:
						i=l[2]
						self.CmdBlk[i]=kwargs[l[0]]
						

					elif l[1]==1 and l[3]!=0 or l[4]!=7:
						i=l[2]
						self.CmdBlk[i]=kwargs[l[0]]
						
					
		x= cdbformat[kwargs['opcode']]['format']	
    		count = Counter((i[2]) for i in x)
    		out = [i for i in x if count[(i[2])] > 1]
		d={}
		for i in out:
			bit=[0,0,0,0,0,0,0,0]
			for j in out:
				if i[2]==j[2] and i[0]!=j[0]:
					if i[2] in d.keys():
						break
					else:
						d[i[2]]=bit
						if i[3]==i[4]:
							bit[i[3]]=kwargs[i[0]]
							
						else:
							s1=bin(kwargs[i[0]])[2:]
							num1=[int(s1[m],2) for m in range(0,len(s1))]
							m=0
							for k in range(i[3],i[4]+1):
								bit[k]=num1[m]
								m=m+1
							
				 							
						if j[3]==j[4]:
							bit[j[3]]=kwargs[j[0]]
							
						else:
							s2=bin(kwargs[j[0]])[2:]
							num2=[int(s2[m],2) for m in range(0,len(s2))]
							m=0
							for k in range(j[3],j[4]+1):
								bit[k]=num2[m]
								m=m+1
							
		
		for k in d.keys():
			d[k].reverse()
			s=""
			for m in range(0,len(d[k])):
				s=s+str(d[k][m])
			self.CmdBlk[k]= int(s,2)
				
		if dx==-2:
			self.Buff.value=kwargs['data']
			self.indata=kwargs['data']
		else:
			self.indata=""
		if cdbformat[kwargs['opcode']]['TR_LEN']==1:
			self.tlen=kwargs['t_length']
		else:
			self.tlen=r			
			

		self.io_hdr= SgIoHdr(interface_id=ord('S'),
				     dxfer_direction = dx,
				     cmd_len = sizeof(self.CmdBlk),
				     iovec_count = 0,
				     mx_sb_len = sizeof(self.sense_buffer),
				     dxfer_len = self.tlen,
				     cmdp = cast(self.CmdBlk, c_void_p),
				     dxferp = cast(self.Buff, c_void_p),
                                     sbp = cast(self.sense_buffer, c_void_p),
                                     timeout = cdbformat[kwargs['opcode']]['timeout'])

	def loadlib(self,lib):
		self.libinquiry = cdll.LoadLibrary(lib)
		self.sg_inquiry=self.libinquiry.sg_inquiry
		self.sg_inquiry.argtypes = (POINTER(SgIoHdr),POINTER(c_char),c_char_p,c_int)
		self.sg_inquiry.restype = c_int


	def call(self):
		self.ret=self.sg_inquiry(byref(self.io_hdr),self.indata,self.ptrdata,self.tlen)
		return self.ret,self.ptrdata.value

		

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

dataformat={"PQual":[1,0,5,7,'b'],"Device_type":[1,0,0,4,'b'],"RMB":[1,1,7,7,'b'],"Version":[1,2,0,0,'h'],"Vendor_identification":[8,8,0,0,'s'],"Product_identification":[8,16,0,0,'s'],"Product_revision_level":[4,32,0,0,'s'],"Page_code":[1,1,0,0,'h']}

sensetype={0x70:"fixed format, current sense",0x71:"fixed format, previous sense",0x72:"descriptor format, current sense",0x73:"descriptor format, previous sense"}

sensekey={0x0:"No sense",0x1:"Recovered Error ",0x2:"Not Ready",0x3:"Medium Error",0x4:"Hardware Error",0x5:"Illegal Request",0x6:"Unit Attention",0x7:"Data Protect ",0x9:"Blank Check",0xA:"Vendor Specific",0xB:"Copy Aborted",0xC:"Aborted Command",0xD:"Volume Overflow",0xE:""}

ASC_ASCQ={(0x00, 0x00): "No Additional Sense Information",
(0x01, 0x00): "No Index/Logical Block Signal",
(0x02, 0x00):" No SEEK Complete",
(0x03, 0x00):" Peripheral Device Write Fault",
(0x03, 0x86):" Write Fault Data Corruption",
(0x04, 0x00):" Logical Unit Not Ready, Cause Not Reportable",
(0x04, 0x01):" Logical Unit Not Ready, Becoming Ready",
(0x04, 0x02):" Logical Unit Not Ready, START UNIT Required",
(0x04, 0x03):" Logical Unit Not Ready, Manual Intervention Required",
(0x04, 0x04):" Logical Unit Not Ready, Format in Progress",
(0x04, 0x09):"Logical Unit Not Ready, Self Test in Progress",
(0x04, 0x0A):"Logical Unit Not Ready, NVC recovery in progress after and exception event",
(0x04, 0x11):" Logical Unit Not Ready, Notify (Enable Spinup) required",
(0x04, 0xF0):" Logical unit not ready, super certify in progress",
(0x08, 0x00):" Logical Unit Communication Failure",
(0x08, 0x01):" Logical Unit Communication Time-Out",
(0x08, 0x02):" Logical Unit Communication Parity Error",
(0x09, 0x00):" Track Following Error",
(0x09, 0x01):" Servo Fault",
(0x09, 0x04):" Head Select Fault",
(0x09, 0x0D):" Write to at least one copy of a redundant file failed",
(0x09, 0x0E):" Redundant files have < 50% good copies",
(0x09, 0xF8):" Calibration is needed but the QST is set without the Recall Only bit",
(0x09, 0xFF):" Servo Cal completed as part of self-test",
(0x0A, 0x00):" Error Log Overflow",
(0x0A, 0x01):" Failed to write super certify log file",
(0x0A, 0x02):" Failed to read super certify log file",
(0x0B, 0x00):" Aborted Command ",
(0x0B, 0x01):" Warning Specified Temperature Exceeded",
(0x0B, 0x02):" Warning, Enclosure Degraded",
(0x0C, 0x00):" Write Error",
(0x0C, 0x01):" Write Error Recovered With Auto-Reallocation",
(0x0C, 0x02):" Write Error Auto Reallocation Failed",
(0x0C, 0x03):" Write Error Recommend Reassignment",
(0x0C, 0xFF):" Write Error Too much error recovery revs",
(0x0D, 0x00):" Volume Overflow Constants",
(0x0E, 0x00):" Data Miscompare",
(0x10, 0x00):" ID CRC Or ECC Error ",
(0x11, 0x00):" Unrecovered Read Error",
(0x11, 0x01):" Read Retries Exhausted",
(0x11, 0x02):" Error Too Long To Correct",
(0x11, 0x04):" Unrecovered Read Error Auto Reallocation Failed",
(0x11, 0xFF):" Unrecovered Read Error Too many error recovery revs",
(0x12, 0x00):" Address Mark Not Found For ID Field",
(0x12, 0x01):" Recovered Data Without ECC Using Previous Logical Block ID",
(0x12, 0x02):" Recovered Data With ECC Using Previous Logical Block ID",
(0x14, 0x00):" Logical Block Not Found",
(0x14, 0x01):" Record Not Found",
(0x15, 0x00):" Random Positioning Error",
(0x15, 0x01):" Mechanical Positioning Error",
(0x15, 0x02):" Positioning Error Detected By Read Of Medium",
(0x16, 0x00):" Data Synchronization Mark Error",
(0x17, 0x00):" Recovered Data With No Error Correction Applied",
(0x17, 0x01):" Recovered Data Using Retries",
(0x17, 0x02):" Recovered Data Using Positive Offset",
(0x17, 0x03):" Recovered Data Using Negative Offset",
(0x17, 0x05):" Recovered Data Using Previous Logical Block ID",
(0x17, 0x06):" Recovered Data Without ECC Data Auto Reallocated",
(0x18, 0x00):" Recovered Data With ECC",
(0x18, 0x01):" Recovered Data With ECC And Retries Applied",
(0x18, 0x02):" Recovered Data With ECC And Or Retries, Data Auto-Reallocated",
(0x18, 0x05):" Recovered Data Recommand Reassignment",
(0x18, 0x06):" Recovered Data Using ECC and Offsets ",
(0x18, 0x07):" Recovered Data With ECC Data Rewritten",
(0x19, 0x00):" Defect List Error",
(0x19, 0x01):" Defect List Not Available", 
(0x19, 0x02):" Defect List Error In Primary List",
(0x19, 0x03):" Defect List Error in Grown List",
(0x19, 0x0E):" Fewer than 50% Defect List Copies",
(0x1A, 0x00):" Parameter List Length Error",
(0x1B, 0x00):" Synchronous Data Transfer Error",
(0x1C, 0x00):" Defect List Not Found",
(0x1C, 0x01):" Primary Defect List Not Found",
(0x1C, 0x02):" Grown Defect List Not Found",
(0x1C, 0x83):" Seagate Unique Diagnostic Code",
(0x1D, 0x00):" Miscompare During Verify Operation",
(0x1F, 0x00):" Number of Defects Overflows the Allocated Space That The Read Defect Command Can Handle",
(0x20, 0x00):" Invalid Command Operation Code",
(0x20, 0xF3):" Invalid linked command operation code",
(0x21, 0x00):" Logical Block Address Out Of Range",
(0x24, 0x00):" Invalid Field In CDB",
(0x24, 0x01):" Illegal Queue Type for CDB (Low priority commands must be SIMPLE queue)",
(0x24, 0xF0):" Invalid LBA in linked command",
(0x24, 0xF2):" Invalid linked command operation code",
(0x24, 0xF3):" Illegal G->P operation request",
(0x25, 0x00):" Logical Unit Not Supported",
(0x26, 0x00):" Invalid Field In Parameter List",
(0x26, 0x01):" Parameter Not Supported",
(0x26, 0x02):" Parameter Value Invalid",
(0x26, 0x03):" Invalid Field Parameter Threshold Parameter",
(0x26, 0x04):" Invalid Release of Active Persistent Reserve",
(0x26, 0x05):" Fail to read valid log dump data",
(0x26, 0x97):" Invalid Field Parameter TMS Firmware Tag",
(0x26, 0x98):" Invalid Field Parameter Check Sum",
(0x26, 0x99):" Invalid Field Parameter Firmware Tag",
(0x27, 0x00):" Write Protected",
(0x29, 0x00):" Flashing LED occurred",
(0x29, 0x00):" Power On, Reset, Or Bus Device Reset Occurred",
(0x29, 0x01):" Power-On Reset Occurred",
(0x29, 0x02):" SCSI Bus Reset Occurred",
(0x29, 0x03):" Bus Device Reset Function Occurred",
(0x29, 0x04):" Internal Reset Occurred",
(0x29, 0x05):" Transceiver Mode Changed To Single-Ended",
(0x29, 0x06):" Transceiver Mode Changed To LVD",
(0x29, 0x07):" Write Log Dump data to disk successful OR IT Nexus Loss",
(0x29, 0x08):" Write Log Dump data to disk fail",
(0x29, 0x09):" Write Log Dump Entry information fail",
(0x29, 0x0A):" Reserved disc space is full",
(0x29, 0x0B):" SDBP test service contained an error, examine status packet(s) for details",
(0x29, 0x0C):" SDBP incoming buffer overflow (incoming packet too big)",
(0x29, 0xCD):" Flashing LED occurred. (Cold reset)",
(0x29, 0xCE):" Flashing LED occurred. (Warm reset)",
(0x2A, 0x01):" Mode Parameters Changed",
(0x2A, 0x02):" Log Parameters Changed",
(0x2A, 0x03):" Reservations preempted",
(0x2A, 0x04):" Reservations Released",
(0x2A, 0x05):" Registrations Preempted",
(0x2C, 0x00):" Command Sequence Error",
(0x2F, 0x00):" Tagged Commands Cleared By Another Initiator",
(0x31, 0x00):" Medium Format Corrupted",
(0x31, 0x01):" Corruption in R/W format request",
(0x31, 0x91):" Corrupt World Wide Name (WWN) in drive information file",
(0x32, 0x00):" No Defect Spare Location Available",
(0x32, 0x01):" Defect List Update Error",
(0x32, 0x02):" No Spares Available Too Many Defects On One Track",
(0x32, 0x03):" Defect list longer than allocated memory",
(0x33, 0x00):" Flash not ready for access",
(0x35, 0x00):" Unspecified Enclosure Services Failure",
(0x35, 0x01):" Unsupported Enclosure Function",
(0x35, 0x02):" Enclosure Services Unavailable",
(0x35, 0x03):" Enclosure Transfer Failure",
(0x35, 0x04):" Enclosure Transfer Refused",
(0x37, 0x00):"Parameter Rounded",
(0x3D, 0x00):" Invalid Bits In Identify Message",
(0x3E, 0x03):" Logical Unit Failed Self Test",
(0x3E, 0x00):" Logical Unit Has Not Self Configured Yet",
(0x3F, 0x00):" Target Operating Conditions Have Changed",
(0x3F, 0x01):" Device internal reset occurred",
(0x3F, 0x02):" Changed Operating Definition",
(0x3F, 0x05):" Device Identifier Changed",
(0x3F, 0x0F):" Echo buffer overwritten",
(0x3F, 0x80):" Buffer contents have changed",
(0x3F, 0x90):"Invalid APM Parameters",
(0x3F, 0x91):" World Wide Name (WWN) Mismatch",
(0x40, 0x01):" DRAM Parity Error",
(0x40, 0x02):" Spinup Error recovered with retries",
(0x42, 0x00):" Power-On Or Self-Test Failure",
(0x42, 0x0A):" Port A failed loopback test",
(0x42, 0x0B):"Port B failed loopback test",
(0x43, 0x00):" Message Reject Error B",
(0x44, 0x00):" Internal Target Failure",
(0x44, 0xF2):" Data Integrity Check Failed on verify",
(0x44, 0xF6):" Data Integrity Check Failed during write",
(0x44, 0xFF):" XOR CDB check error",
(0x45, 0x00):" Select/Reselection Failure",
(0x47, 0x00):"SCSI Parity Error",
(0x47, 0x03):"Information Unit CRC Error ",
(0x47, 0x80):"Fibre Channel Sequence Error",
(0x48, 0x00):" Initiator Detected Error Message Received ",
(0x49, 0x00):" Invalid Message Received",
(0x4B, 0x00):" Data Phase Error",
(0x4B, 0x01):" Invalid transfer tag",
(0x4B, 0x02):" Too many write data",
(0x4B, 0x03):"ACK NAK Timeout",
 (0x4B, 0x04):" NAK received",
(0x4B, 0x00):" Data Offset error",
(0x4B, 0x06):" Initiator response timeout",
(0x4C, 0x00):" Logical Unit Failed Self-Configuration",
(0x4E, 0x00):" Overlapped Commands Attempted",
(0x55, 0x01):" XOR Cache is Not Available",
(0x55, 0x04):" PRKT table is full",
(0x5B, 0x00):"Log Exception ",
(0x5B, 0x01):"Threshold Condition Met",
(0x5B, 0x02):" Log Counter At Maximum",
(0x5B, 0x03):" Log List Codes Exhausted",
(0x5C, 0x00):" RPL Status Change",
(0x5C, 0x01):" Spindles Synchronized",
(0x5C, 0x02):" Spindles Not Synchronized",
(0x5D, 0x00):" Failure Prediction Threshold Exceeded",
 (0x5D, 0xFF):" False Failure Prediction Threshold Exceeded",
(0x65, 0x00):" Voltage Fault",
(0x80, 0x00):" General Firmware Error Qualifier",
 (0x80,0x86):" IOEDC Error on Read",
(0x80, 0x87):"IOEDC Error on Write",
(0x80, 0x88):" Host Parity Check Failed",
 (0x80, 0x89):" IOEDC Error on Read Detected by Formatter",
 (0x80, 0x8A):" Host FIFO Parity Error detected by Common Buffer",
(0x80, 0x8B):" Host FIFO Parity Error detected by frame buffer logic",
 (0x80, 0x8C):" Host Data Frame Buffer Parity Error",
 (0x81, 0x00):" Reassign Power Fail Recovery Failed",
 (0x81, 0x00):" LA Check Error, LCM bit = 0 4 81 00 LA Check Error",
 (0xB4, 0x00):" Unreported Deferred Errors have been logged on log page 34h"}

class Sensedata:
	def __init__(self,sensetype,sensekey,ASC_ASCQ):
		self.sensetype=sensetype
		self.sensekey=sensekey
		self.ASC_ASCQ=ASC_ASCQ
	
	def ptr_addr(self,ptr,offset):
		x=addressof(ptr.contents)+offset
		return pointer(type(ptr.contents).from_address(x))
	
	def getSensetype(self,ptr):
		st=ptr.contents.value
		r=bin(ord(st))[2:].zfill(8)		
		s1=hex(int(r[1:],2))
		for k,v in sensetype.items():
			if s1==hex(k):
				return v
			
	def getSensekey(self,ptr):
		m=self.ptr_addr(ptr,2)
		st=m.contents.value
		r=bin(ord(st))[2:].zfill(8)		
		s1=hex(int(r[5:],2))
		for k,v in sensekey.items():
			if s1==hex(k):
				return v


	def getASC_ASCQ(self,ptr):
		m=self.ptr_addr(ptr,12)
		st=m.contents.value
		r=bin(ord(st))[2:].zfill(8)
		s1=hex(int(r,2))
		m=self.ptr_addr(ptr,13)
		st=m.contents.value
		r=bin(ord(st))[2:].zfill(8)		
		s2=hex(int(r,2))
		for k,v in ASC_ASCQ.items():
			if s1==hex(k[0]) and s2==hex(k[1]):
				return v

'''s=Sensedata(sensetype,sensekey,ASC_ASCQ)
print s.getSensetype(t)
print s.getSensekey(t)
print s.getASC_ASCQ(t)'''

if __name__ == "__main__":
	import pdb
	#pdb.set_trace()
	c=CDB(opcode='0x0a',lba=0,t_length=10,control=0,data="hello")
	c.loadlib('./libinquiry.so.1.0')
	c.call()




