import hug
# need to install from github
# https://github.com/digitalhurricane-io/haproxyadmin.git
from haproxyadmin import haproxy
from falcon import HTTP_204

# To authenticate with API using basic auth
USERNAME = 'admin'
PASSWORD = 'admin'
# Location of haproxy socket in docker container (bind mount to wherever the socket is on your main machine)
HAPROXY_SOCKET_DIR = '/socket_dir'


authentication = hug.authentication.basic(hug.authentication.verify(USERNAME, PASSWORD))
hap = haproxy.HAProxy(socket_dir=HAPROXY_SOCKET_DIR)


@hug.get('/stats/frontends/bytes_out', requires=authentication)
def get_frontend_outgoing_bandwidth():
    '''
    Returns outgoing bandwidth for all frontends in bytes
    '''
    b = {}
    frontends = hap.frontends()
    for frontend in frontends:
        b.update({frontend.name:frontend.metric('bout')})

    return b


@hug.get('/backends', requires=authentication)
def get_backend_names():
    return [backend.name for backend in hap.backends()]


@hug.put('/backends/servers/update', requires=authentication)
def update(backend_name:hug.types.text, 
            server_name: hug.types.text, 
            enabled: hug.types.boolean, 
            ip_and_port: hug.types.text,
            response):
    '''
    Updates a backend server
    '''
    try:
        all_backends = hap.backends()
    except:
        return {'error': 'could not retrieve backends. ensure socket_dir is set to the correct path'}

    try:
        backend = all_backends[all_backends.index(backend_name)]
    except:
        return {'error': 'could not find specified backend'}

    try:
        server = [server for server in backend.servers() if server.name == server_name][0]
    except:
        return {'error': 'could not find specified server'}

    server.setaddress(ip_and_port)

    if enabled:
        successful = server.setstate('enable')
        if not successful:
            return {'error': 'failed to enable server'}
    else:
        successful = server.setstate('disable')
        if not successful:
            return {'error': 'failed to disable server'}

    response.status = HTTP_204
    
    
