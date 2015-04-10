from command2 import CDB, Response
from ctypes import *


class cdbLibrary(object):

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    dataformat={"PQual":[1,0,5,7,'b'],"Device_type":[1,0,0,4,'b'],"RMB":[1,1,7,7,'b'],"Version":[1,2,0,0,'h'],"Vendor_identification":[8,8,0,0,'s'],"Product_identification":[8,16,0,0,'s'],"Product_revision_level":[4,32,0,0,'s'],"Page_code":[1,1,0,0,'h']}

    def inquiry(self,opcode,CMDDT,EVDT,pagecode,alloclen,control,EV1):
	self._cdb=CDB(opcode=opcode,CMDDT=CMDDT,EVDT=EVDT,pagecode=pagecode,alloclen=alloclen,control=control,EV1=EV1)      
        self._cdb.loadlib('./libinquiry.so.1.0')
	self.result=self._cdb.call()

    def inquiryPQual(self,field):
	res=Response(self.dataformat)
	self.t=cast(self._cdb.io_hdr.dxferp,POINTER(c_char))
	return res.getResponse(self.t,field)


    def result_should_be(self, success):
	if self.wrres[0] != success:
        	raise AssertionError('%s != %s' % (self.wrres[0], success))

    def binresponse_should_be(self,res,success):
	res=int(res)
	if res != success:
        	raise AssertionError('%s != %s' % (res, success))

    def data_should_be(self,res,success):
	print res,success
	if res[1] != success:
        	raise AssertionError('%s != %s' % (res, success))


    def write6(self,opcode,lba,t_length,control,data):
	self._cdb=CDB(opcode=opcode,lba=lba,t_length=t_length,control=control,data=data)
	self._cdb.loadlib('./libinquiry.so.1.0')
	self.wrres=self._cdb.call()


    def read6(self,opcode,lba,t_length,control):
	self._cdb=CDB(opcode=opcode,lba=lba,t_length=t_length,control=control)
	self._cdb.loadlib('./libinquiry.so.1.0')
	self.readres,self.outdata=self._cdb.call()
	return self.readres,self.outdata


if __name__ == "__main__":
	import pdb
	#pdb.set_trace()
	c=cdbLibrary()	
	c.write6('0x0a',0,10,0,"hello")
	a,b=c.read6('0x08',0,10,0)
	c.inquiry('0x12',0,1,0,96,0,1)
	'''print c.result, type(c.result)
	l=c.inquiryPQual("PQual")
	print l,type(l),type(0)
	c.result_should_be(0)'''






