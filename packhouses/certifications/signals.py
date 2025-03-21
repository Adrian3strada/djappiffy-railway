from django.dispatch import receiver

@receiver()
def prueba(sender, **kwargs)
    print("Funciona")