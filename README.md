**English speakers: we expect most of our users to be french. If you want to implement an api.taxi operator but are not a french speaker, please create an issue in this repository  and we'll translate this document.**

# minimal_operateur_server

Ce projet est un exemple de serveur opérateur utilisé dans le cadre du registre [api.taxi](https://le.taxi/).

Les opérateurs agréés qui envoient la localisation de leurs taxis doivent mettre en place une API permettant de traiter les demandes de courses.

Lorsque le registre *api.taxi* reçoit une demande de course, une requête est effectuée sur l'API de l'opérateur pour l'en informer. L'opérateur doit notifier le taxi de la demande de course, qui peut l'accepter ou la refuser.

Vous trouverez plus de détails sur la page de [documentation](https://api.taxi/documentation) de votre console d'administration.

## Utilisation

* Éditez le fichier `settings.py` et renseignez votre token d'API dans la variable `API_TAXI_KEY`. Si vous travaillez sur l'environnement de développement, vous devrez modifier `API_TAXI_URL` pour renseigner `https://dev.api.taxi`.
* Lancez les containers avec `docker-compose up`

## Fonctionnement

La section **Mon compte** de la console d'administration *api.taxi* permet de renseigner une URL vers l'endpoint d'acceptation des courses de l'API opérateur.

Lorsqu'une demande de course arrive sur les serveurs du registre *api.taxi*, une requête `POST` est faite vers cet endpoint. Elle contient le payload suivant :

```
{
    data: [{
        'customer_lon': <longitude du client>,
        'customer_lat': <latitude du client>,
        'customer_address': <adresse du client>,
        'customer_phone_number': <numéro de téléphone du client>,
        'id': <identifiant de la course (aussi appelée "hail")>,
        'taxi': {
            'id': <identifiant du taxi>,
        }
    }]
}
```

L'opérateur doit alors effectuer les actions suivantes :

* retourner une réponse HTTP/200 pour informer que la demande bien été prise en compte
* informer le taxi de la demande
* une fois le taxi informé, appeler l'endpoint `PUT /hails/:id` de *api.taxi* afin de mettre le statut de la course à `received_by_taxi`. Si le statut n'est pas mis avant 10 secondes, la course est automatiquement annulée.
	- si le taxi accepte la course, appeler l'endpoint `PUT /hails/:id` de *api.taxi* et mettre le statut de la course à `accepted_by_taxi`, en fournissant le numéro de téléphone du taxi dans le champ `taxi_phone_number`.
	- si le taxi refuse la course, mettre le statut de la course à `declined_by_taxi`.
	- si le statut de la course n'est pas mis à jour avant 30 secondes, la course est automatiquement annulée.

Pour plus d'informations, consultez la [documentation](https://api.taxi/documentation) de votre console d'administration.

## Limitations

Ce serveur d'exemple accepte toutes les courses. Son intérêt est de présenter une API simple et commentée sur laquelle vous pouvez vous baser pour effectuer l'intégration de votre solution. Il sera donc à votre charge d'implémenter la notification de demande de course.

## Modules utilisés

* [flask](https://flask.palletsprojects.com) est un des frameworks Python les plus connus pour développer une application web
* [rq](https://python-rq.org/) et le module Flask correspondant [flask-rq2](https://flask-rq2.readthedocs.io) est utilisé pour effectuer des requêtes asynchrones. La notification de la course au taxi ainsi que la mise à jour du statut de la course son faits de manière asynchrone par un worker.
