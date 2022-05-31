import os
import re
import grpc

from sqlflow import Client, StreamReader
from sqlflow.env_expand import EnvExpander, EnvExpanderError
from sqlflow.compound_message import CompoundMessage
from sqlflow.rows import Rows

from bs4 import BeautifulSoup

if not os.environ.get("SQLFLOW_SERVER"):
    os.environ['SQLFLOW_DATASOURCE'] = "mysql://root:root@tcp(IP_TO_MYSQL)/?maxAllowedPacket=0"

DEFAULT_TIMEOUT = 3600 * 10


class MyClient(Client):
    def __init__(self, server_url=None, ca_crt=None):
        super().__init__(server_url, ca_crt)

    def execute(self, operation, emit):
        """Run a SQL statement

        :param operation: SQL statement to be executed.
        :type operation: str.

        :returns: sqlflow.client.Rows

        Example:

        >>> client.execute("select * from iris limit 1")

        """
        try:
            stream_response = self._stub.Run(self.sql_request(operation), timeout=DEFAULT_TIMEOUT)
            return self.display(stream_response, emit)
        except grpc.RpcError as e:
            # NOTE: raise exception to interrupt notebook execution. Or
            # the notebook will continue execute the next block.
            raise e
        except EnvExpanderError as e:
            raise e
        
    def parse_html(self, first_line, stream_reader):
        resp_list = [first_line]
        for res in stream_reader.read_until_type_changed():
            resp_list.append(res.message.message)
        soup = BeautifulSoup(resp_list[0], "html.parser")
        images = soup.findAll('img')[0]
        return images['src']

    def display(self, stream_response, emit):
        """Display stream response like log or table.row"""
        reader = StreamReader(stream_response)
        response, rtype = reader.read_one()
        emit('log', "INFO [A]: ")
        print('log', "INFO [A]: ")
        print(response, rtype)
        compound_message = CompoundMessage()
        while True:
            if response is None:
                break
            if rtype == 'message':
                if re.match(r'<[a-z][\s\S]*>.*', response.message.message):
                    emit('log', "INFO [B]: ")
                    print('log', "INFO [B]: ")
                    parsed_response = self.parse_html(response.message.message, reader)
                    emit('img', parsed_response)

                else:
                    emit("INFO [C]: ")
                    emit('log', response.message.message)
                    print(response.message.message)
                    for response in reader.read_until_type_changed():
                        emit('log', response.message.message)
                        print(response.message.message)
                    response = reader.last_response
                    if response is not None:
                        rtype = response.WhichOneof('response')
                    continue
            elif rtype == 'job':
                job = response.job
                # the last response type is Job for the workflow mode,
                # so break the loop here
                return self.read_fetch_response(job)
            elif rtype == 'head' or rtype == 'row':
                column_names = [
                    column_name for column_name in response.head.column_names]

                def rows_gen():
                    for res in reader.read_until_type_changed():
                        yield [self._decode_any(a) for a in res.row.data]
                compound_message.add_rows(Rows(column_names, rows_gen), None)
            else:
                # deal with other response type in the future if necessary.
                pass

            # read the next response
            response, rtype = reader.read_one()
        if compound_message.empty():
            # return None to avoid outputing a blank line
            return None
        return compound_message