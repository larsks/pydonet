class AttrDict (dict):
  def __getattr__ (self, k):
    try:
      return self[k]
    except KeyError, detail:
      raise AttributeError(detail)

  def __setattr__ (self, k, v):
    self[k] = v

