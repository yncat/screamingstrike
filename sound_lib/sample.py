from __future__ import absolute_import
import platform
import sys
from .channel import Channel
from .main import bass_call, bass_call_0, FlagObject
from .external.pybass import *

try:
	convert_to_unicode = unicode
except NameError:
	convert_to_unicode = str

class Sample(FlagObject):
	def __init__(self, file, flags=0, unicode=True):
		if platform.system() == 'Darwin':
			unicode = False
			file = file.encode(sys.getfilesystemencoding())
		if unicode and isinstance(file, str):
			file = convert_to_unicode(file)
		self.file = file
		self.setup_flag_mapping()
		flags = flags | self.flags_for(unicode=unicode)
		self.handle = bass_call(BASS_SampleLoad, False, file, 0, 0, 128, flags)

	def __del__(self):
		if self.handle: self.free()

	def free(self):
		return bass_call(BASS_SampleFree, self.handle)

	def setup_flag_mapping(self):
		super(Sample, self).setup_flag_mapping()
		self.flag_mapping.update({
			'unicode': BASS_UNICODE
		})

class SampleBasedChannel(Channel):
	def __init__(self, hsample=None):
		"""Creates a sample-based channel from a sample handle. """
		handle = bass_call(BASS_SampleGetChannel, hsample.handle, False)
		super(SampleBasedChannel, self).__init__(handle)
	def __free__(self):
		pass#Sample-based channels don't have to be explicitly freed; BASS does that
