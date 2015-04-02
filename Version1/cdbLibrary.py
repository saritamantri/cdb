from command1 import CDB, Response
from ctypes import *


class cdbLibrary(object):

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    dataformat={"PQual":[1,0,5,7,'b'],"Device_type":[1,0,0,4,'b'],"RMB":[1,1,7,7,'b'],"Version":[1,2,0,0,'h'],"Vendor_identification":[8,8,0,0,'s'],"Product_identification":[8,16,0,0,'s'],"Product_revision_level":[4,32,0,0,'s'],"Page_code":[1,1,0,0,'h']}

    def inquiry(self,opcode,CMDDT,EVDT,pagecode,allocationlen,control,dxfer,ioveccount,timeout):
	self._cdb = CDB(opcode,CMDDT,EVDT,pagecode,allocationlen,control,dxfer,ioveccount,timeout)
        self._cdb.loadlib('./libinquiry.so.1.0')
	self.result=self._cdb.call()

    def inquiryPQual(self,field):
	res=Response(self.dataformat)
	self.t=cast(self._cdb.io_hdr.dxferp,POINTER(c_char))
	return res.getResponse(self.t,field)


    def result_should_be(self, success):
	if self.result != success:
        	raise AssertionError('%s != %s' % (self.result, success))

    def binresponse_should_be(self,res,success):
	res=int(res)
	if res != success:
        	raise AssertionError('%s != %s' % (res, success))


'''c=cdbLibrary()
c.inquiry(0x12,0,0,0,96,0,-3,0,20000)
print c.result, type(c.result)
l=c.inquiryPQual("PQual")
print l,type(l),type(0)
c.result_should_be(0)'''

