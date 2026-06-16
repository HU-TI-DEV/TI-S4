# Onderzoek ML Gazebo
Dit Onderzoek kijkt naar de mogelijkheden van het implementeren van Machine Learning in Gazebo Jetty.


## Mogelijkheden voor ML in Gazebo
Volgens verschillende websites is het mogelijk om ML te implementeren in Gazebo.(1) Het vereist veel rekenkracht, hierdoor moet je wereld zo optimaal zijn. Ook zijn er verschillende manieren om ML te implementeren in Gazebo, hieronder staan verschillende methoden toegelicht

## reinforment Learning

Er is een demo in Gazebo Jetty, die reinforcemt learning gebruikt. Dat is een vorm van machine learning waarbij een algoritme beslissingen neemt door interactie te maken met alles in de omgeving. Het systeem leert door als de robot bijvoorbeel tegen een muur aanbotst, dat die robot daar dan niet kan rijden.(2)


## ML buiten Gazebo 
Een andere mogelijkheid is dat je sensoren op je robot zet, d ie vervolgens uitlezen via Gazebo transport. Deze gegevens vervolgens verwerkt met PyTorch of TensorFlow en de commando die hieruit ontstaan, terug sturen naar FLip.(3)

## bronnen
1. https://karelics.fi/blog/2021/02/15/using-gazebo-for-reinforcement-learning/
2. https://gazebosim.org/docs/latest/release_notes/
3. https://gazebosim.org/docs/latest/sensors/