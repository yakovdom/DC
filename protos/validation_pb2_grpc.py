# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import validation_pb2 as validation__pb2


class ValidatorStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Validate = channel.unary_unary(
                '/Validator/Validate',
                request_serializer=validation__pb2.ValidationRequest.SerializeToString,
                response_deserializer=validation__pb2.ValidationResponse.FromString,
                )


class ValidatorServicer(object):
    """Missing associated documentation comment in .proto file"""

    def Validate(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ValidatorServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Validate': grpc.unary_unary_rpc_method_handler(
                    servicer.Validate,
                    request_deserializer=validation__pb2.ValidationRequest.FromString,
                    response_serializer=validation__pb2.ValidationResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Validator', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Validator(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def Validate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Validator/Validate',
            validation__pb2.ValidationRequest.SerializeToString,
            validation__pb2.ValidationResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)
