import micromagneticmodel as mm

class MicromagneticData:
	
	def __init__(self, data):

		if isinstance(data, mm.System):
			self.name = data.name
		elif isinstance(data, str):
			self.name = data
		else:
			raise TypeError("Accept only mm.System or string")