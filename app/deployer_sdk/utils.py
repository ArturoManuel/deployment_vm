



def password_authentication_with_scoped_authorization(
    keystone_endpoint,
    user_domain_name,
    username,
    password,
    project_domain_name,
    project_name,
):
    data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": username,
                        "domain": {"name": user_domain_name},
                        "password": password,
                    }
                },
            },
            "scope": {
                "project": {
                    "name": project_name,
                    "domain": {"name": project_domain_name},
                }
            },
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{keystone_endpoint}/auth/tokens", headers=headers, json=data
    )
    return response


def token_authentication_with_scoped_authorization(
    keystone_endpoint,
    admin_token,
    project_domain_name,
    project_name,
):
    data = {
        "auth": {
            "identity": {
                "methods": ["token"],
                "token": {"id": admin_token},
            },
            "scope": {
                "project": {
                    "name": project_name,
                    "domain": {"name": project_domain_name},
                }
            },
        }
    }
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": admin_token,
    }
    response = requests.post(
        f"{keystone_endpoint}/auth/tokens", headers=headers, json=data
    )
    return response




def authenticate_admin():
    response = password_authentication_with_scoped_authorization(
        KEYSTONE_ENDPOINT,
        ADMIN_USER_DOMAIN_NAME,
        ADMIN_USER_USERNAME,
        ADMIN_USER_PASSWORD,
        ADMIN_USER_DOMAIN_NAME,
        ADMIN_PROJECT_NAME,
    )
    if response.status_code == 201:
        print("Autenticación de administrador exitosa.")
        return response.headers["X-Subject-Token"]
    else:
        raise Exception("Error en la autenticación de administrador")

def authenticate_project(admin_token):
    response = token_authentication_with_scoped_authorization(
        KEYSTONE_ENDPOINT,
        admin_token,
        ADMIN_USER_DOMAIN_NAME,
        PROJECT_NAME,
    )
    if response.status_code == 201:
        print(f"Autenticación del proyecto '{PROJECT_NAME}' exitosa.")
        return response.headers["X-Subject-Token"]
    else:
        raise Exception(f"Error en la autenticación del proyecto '{PROJECT_NAME}'")

def create_network_and_subnet(token, network_name, subnet_cidr):
    network_resp = create_network(NEUTRON_ENDPOINT, token, network_name)
    if network_resp.status_code == 201:
        network_data = network_resp.json()
        network_id = network_data["network"]["id"]
        print(f"Red '{network_name}' creada con éxito, ID: {network_id}")

        subnet_resp = create_subnet(
            NEUTRON_ENDPOINT,
            token,
            network_id,
            f"subnet_{network_name}",
            "4",
            subnet_cidr,
        )
        if subnet_resp.status_code == 201:
            subnet_data = subnet_resp.json()
            subnet_id = subnet_data["subnet"]["id"]
            print(f"Subred '{network_name}_subnet' creada con éxito, ID: {subnet_id}")
            return network_id, subnet_id
        else:
            print("Error al crear la subred.")
    else:
        print("Error al crear la red.")
    return None, None

def create_instance_port(token, network_id, port_name):
    port_resp = create_port(NEUTRON_ENDPOINT, token, port_name, network_id, PROJECT_ID)
    if port_resp.status_code == 201:
        port_data = port_resp.json()
        port_id = port_data["port"]["id"]
        print(f"Puerto '{port_name}' creado con éxito, ID: {port_id}")
        return port_id
    else:
        raise Exception(f"Error al crear el puerto '{port_name}'.")

def create_ring_topology(json_data):
    print("Iniciando creación de topología en anillo...")
    admin_token = authenticate_admin()
    project_token = authenticate_project(admin_token)

    node_ports = {}
    subnet_cidr_template = '10.0.{subnet_index}.0/24'

    # Create networks and ports for each link in the ring
    for i, link in enumerate(json_data['topology']['links']):
        link_id = link['link_id']
        source = link['source']
        target = link['target']
        network_name = link_id
        subnet_cidr = subnet_cidr_template.format(subnet_index=i+1)

        # Create network and subnet for this link
        network_id, subnet_id = create_network_and_subnet(project_token, network_name, subnet_cidr)
        if network_id is None:
            continue

        # Create port for the source node on this link
        port_name_source = f"port_{source}_{link_id}"
        port_id_source = create_instance_port(project_token, network_id, port_name_source)
        if port_id_source:
            if source not in node_ports:
                node_ports[source] = []
            node_ports[source].append(port_id_source)

        # Create port for the target node on this link
        port_name_target = f"port_{target}_{link_id}"
        port_id_target = create_instance_port(project_token, network_id, port_name_target)
        if port_id_target:
            if target not in node_ports:
                node_ports[target] = []
            node_ports[target].append(port_id_target)

    # Launch instances with the connected ports
    for node in json_data['topology']['nodes']:
        node_id = node['node_id']
        node_name = node['name']
        networks = [{"port": port_id} for port_id in node_ports.get(node_id, [])]
        print(f"Lanzando instancia '{node_name}' con los puertos {node_ports.get(node_id, [])}...")
        create_instance(NOVA_ENDPOINT, project_token, node_name, FLAVOR_ID, IMAGE_ID, networks)
        print(f"Instancia '{node_name}' lanzada con éxito.")
