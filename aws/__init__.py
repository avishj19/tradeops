"""AWS package: embedded cloud contract for TradeOps agents."""
from .adapter import AWSAdapter, LocalAWSMirror, aws_config_from_env, embed_run_in_aws, get_aws_backend

__all__ = ['AWSAdapter', 'LocalAWSMirror', 'aws_config_from_env', 'embed_run_in_aws', 'get_aws_backend']
