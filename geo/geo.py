from geopy.geocoders import Nominatim

if __name__ == '__main__':
    address = 'Belarmino Vilela Junqueira, Ituiutaba, MG'
    user_agent = 'Search1'
    location = Nominatim(user_agent=user_agent).geocode(address)
    if location:  # Verifica se a localização foi encontrada
        print(location.latitude, location.longitude)
    else:
        print("Endereço não encontrado.")
