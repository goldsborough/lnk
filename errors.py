class Error(Exception):
	def __init__(self, what, **additional):
		self.what = "\a\033[31;4mError\033[0m: {}".format(what)

		self.verbose = self.what

		for i, j in additional.items():
			self.verbose += "\n\a\033[31;{}\033[0m: {}".format(i, j)

		super(Error, self).__init__(self.what)

class APIError(Error):
	def __init__(self, what, code=None, status=None):
		super(APIError, self).__init__(what, Code=code, Status=status)

class URLError(Error):
	def __init__(self, what="No URL supplied!"):
		super(URLError, self).__init__(what)