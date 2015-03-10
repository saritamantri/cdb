from command1 import CDB


class cdbLibrary(object):
      
    def inquiry(self,opcode,CMDDT,EVDT,pagecode,reply_len,control,dxfer,count,to):
	self._cdb = CDB(opcode,CMDDT,EVDT,pagecode,reply_len,control,dxfer,count,to)
        self._cdb.loadlib('./libinquiry.so.1.0')
	self._result=self._cdb.call()
	

    def result_should_be(self, expected):
	if self._result != expected:
        	raise AssertionError('%s != %s' % (self._result, expected))




    
