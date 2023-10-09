CREATE TABLE portfolio (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Quantité DECIMAL(10, 2),
    PRU DECIMAL(10, 2),
    Cours DECIMAL(10, 2),
    Valo DECIMAL(10, 2),
    `+/-Val` DECIMAL(10, 2),
    `var/PRU` DECIMAL(10, 2),
    `var/Veille` DECIMAL(10, 2),
    `%` DECIMAL(5, 2),
    `Ordre Limite` DECIMAL(10, 2),
    Total DECIMAL(10, 2),
    Currency VARCHAR(50),
    `Time of Update` DATETIME
);