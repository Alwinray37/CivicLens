class PipelineError(Exception):
    pass

class StageFailedError(PipelineError):
    pass