Se opta inicialmente por trabajar 2 flujos separados, uno que llega hasta el envio de correo de bienvenida si se decide continuar con el candidato y cual se le agregara la funcion de que el candidato acepte, y otro que gerera el correo de notificacion de credenciales y responsabilidades

### ETAPA 1

en primera instancia se corre el archivo etapa1.py, este archivo va desde la extracion de los datos de entrada hasta la emision del correo de bienvenida  basados en en la AI de Gemini y Lancgchain, los datos de entrada datos deben estar ubicados dentro de la carpeta de output, cada candidato debe tener su carpeta con tres archivos obligatorios, entrevista transcrita, cv en pdf y archivo de metadata.
![image](https://github.com/user-attachments/assets/e6ab7342-fdd5-4a5c-9a70-5bc335d1ffed)

![image](https://github.com/user-attachments/assets/e72e39f2-87d8-4dbd-98c8-78763f6ade56)

tantos candidatos haya en la capeta input sera la misma cantidad que se va generando el output en tiempo real.



una vez se corre el archivo etapa1 comenzamos a ver el flujo

![image](https://github.com/user-attachments/assets/fddc76df-eac6-474b-bf6b-3f0e4893eff3)
se genera archivos en output, una minuta (basada en CV y entrevista) y na evaluacion que determina si el candidato continua o no, cabe destacar que estas 

![image](https://github.com/user-attachments/assets/fc68991c-be0a-425a-b366-b29d2d12c326)

en este punto el usuario tiene la opcion de continuar con el proceso del candidato independientemente de la decision que muestre la terminal

si se opta por continuar con el proceso se genera de manera inmediata un correo de vuelta de bienvenida en formato html

![image](https://github.com/user-attachments/assets/6d6545c9-f665-4a4e-a94e-8a270297145c)

si se decide no continuar con el proceso llega un correo de agradecimiento al candidato

![image](https://github.com/user-attachments/assets/881c6a9a-29bc-4047-b34d-5bbb31751992)

### ETAPA 2

La ejecucion del archvo de etapa2.py abarca desde la aceptacion del candidato de continuar en el proceso hasta el envio de un correo con sus credenciales y responsabilidades basadas en su rol.

voilviendo al correo de bienvenida se le indica al candidato que responda el mismo con la palabra "acepto"

![image](https://github.com/user-attachments/assets/34b95ee2-ad92-4ae4-ac9e-74a6c601b3dc)
![image](https://github.com/user-attachments/assets/5be0ab87-acdd-4e9b-8b29-d321c582bf46)


Una vez respondido el correo, y con la ayuda de la herramienta IMAP podemos hacer una revision de correos de respuesta aunque el entorno local este apagado siendo esta una de las mayores ventajas,
encontrado el correo con la respuesta almacenada el sistema pregunta al usuario si desea enviar el correo de credenciales y responsabilidades 
![image](https://github.com/user-attachments/assets/048036ed-6136-4559-bd55-52fc260d8fb2)

(Por ciertas limitaciones en estos momentos el proceso a continuacion tiende a ser manual) 
paso siguiente el sistema pide al usuario ingreso manual del link de credenciales y responsabilidades
![image](https://github.com/user-attachments/assets/5791745b-b89e-46b4-90a7-c21323e3194b)

![image](https://github.com/user-attachments/assets/47cb31c8-982b-4662-8cea-81d2e907ad6a)













