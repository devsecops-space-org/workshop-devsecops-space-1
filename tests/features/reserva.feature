# language: es

Característica: Gestión de reservas de salas de reunión

  Como empleado de la empresa
  Quiero reservar salas de reunión disponibles
  Para organizar reuniones respetando la capacidad y los horarios laborales

  Antecedentes:
    Dado que el sistema gestiona las siguientes salas con sus capacidades máximas:
      | sala | capacidad |
      | A    | 4         |
      | B    | 8         |
      | C    | 20        |
    Y que el horario laboral permitido para reservas es de "08:00" a "20:00"

  Escenario: Flujo principal - Crear una reserva válida, consultarla y verificarla en el listado
    Dado que no existen reservas en el sistema
    Cuando se crea una reserva para la sala "B" el día "2099-06-01" de "10:00" a "11:00" con 5 asistentes y propósito "Revisión semanal del equipo de plataforma"
    Entonces el sistema confirma la creación de la reserva
    Y es posible consultar la reserva por su identificador con los datos registrados
    Y la reserva aparece al listar las reservas de la sala "B"

  Escenario: Flujo principal - Cancelar una reserva futura y verificar que desaparece del listado
    Dado que existe una reserva en la sala "C" el día "2099-06-01" de "14:00" a "15:00" con 10 asistentes y propósito "Presentación trimestral de resultados del área"
    Cuando se cancela la reserva previamente registrada
    Entonces el sistema confirma la cancelación
    Y la reserva ya no aparece al listar las reservas de la sala "C"

  Escenario: Validación - Rechazar reserva que supera la capacidad de la sala
    Cuando se intenta crear una reserva para la sala "A" el día "2099-06-01" de "09:00" a "10:00" con 10 asistentes y propósito "Reunión de todos los equipos del área"
    Entonces el sistema rechaza la operación por superar la capacidad de la sala

  Escenario: Validación - Rechazar reserva con solapamiento de horario en la misma sala y día
    Dado que existe una reserva en la sala "B" el día "2099-06-01" de "10:00" a "11:00" con 5 asistentes y propósito "Revisión semanal del equipo de plataforma"
    Cuando se intenta crear una reserva para la sala "B" el día "2099-06-01" de "10:30" a "11:30" con 4 asistentes y propósito "Seguimiento de proyecto de plataforma"
    Entonces el sistema rechaza la operación por solapamiento de horario

  Escenario: Validación - Rechazar la cancelación de una reserva que ya ocurrió
    Dado que existe una reserva en la sala "A" el día "2000-01-01" de "09:00" a "10:00" con 2 asistentes y propósito "Reunión de inicio del proyecto anual"
    Cuando se cancela la reserva previamente registrada
    Entonces el sistema rechaza la operación por no poder cancelar reservas pasadas

  Esquema del escenario: Validación - Rechazar reserva con datos de horario o propósito inválidos
    Cuando se intenta crear una reserva para la sala "B" el día "2099-06-01" de "<hora_inicio>" a "<hora_fin>" con 3 asistentes y propósito "<proposito>"
    Entonces el sistema rechaza la operación por datos inválidos

    Ejemplos:
      | hora_inicio | hora_fin | proposito                              |
      | 07:00       | 08:30    | Reunión de madrugada del equipo        |
      | 10:00       | 10:10    | Reunión corta de sincronización        |
      | 10:00       | 15:00    | Reunión que excede la duración máxima  |
      | 10:00       | 11:00    | Corto                                  |
      | 11:00       | 10:00    | Reunión con horario invertido del día  |

  Escenario: Caso límite - Listar reservas cuando no existen reservas para la sala solicitada
    Dado que no existen reservas en el sistema
    Cuando se listan las reservas filtrando por la sala "C"
    Entonces el sistema retorna una lista vacía de reservas

  Escenario: Seguridad - Rechazar reserva con propósito que contiene secuencias de inyección
    Cuando se intenta crear una reserva para la sala "B" el día "2099-06-01" de "10:00" a "11:00" con 3 asistentes y propósito "<script>alert('xss')</script>"
    Entonces el sistema rechaza la operación por datos inválidos
