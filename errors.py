
class Error(Exception):
	def __init__(self, what, **additional):

		self.what = "\a\033[91mError\033[0m: {}".format(what)

		self.verbose = self.what

		for i, j in additional.items():
			# Might be None
			if j:
				self.verbose += "\n\033[91m{}\033[0m: {}".format(i, j)

		super().__init__(self.what)

class HTTPError(Error):
	def __init__(self, what, code=None, status=None):

		super().__init__(what, Code=code, Status=status)

class APIError(Error):
	def __init__(self, what, message=None):

		super().__init__(what, Message=message)

def warn(what):

		print("\a\033[93mWarning\033[0m: {}".format(what))
