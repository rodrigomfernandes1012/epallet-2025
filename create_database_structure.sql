-- ============================================
-- Script de Criação do Banco de Dados Epallet
-- Sistema de Gestão de Pallets
-- ============================================
-- 
-- INSTRUÇÕES DE USO:
-- 1. Conectar ao MySQL: mysql -u epallet -p
-- 2. Selecionar banco: USE epallet_db;
-- 3. Executar script: SOURCE create_database_structure.sql;
--
-- Ou executar diretamente:
-- mysql -u epallet -p epallet_db < create_database_structure.sql
-- ============================================

-- Usar banco de dados
USE epallet_db;

-- Desabilitar verificações temporariamente
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- TABELA: tipos_empresa
-- ============================================
DROP TABLE IF EXISTS tipos_empresa;

CREATE TABLE tipos_empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nome (nome),
    INDEX idx_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inserir tipos padrão
INSERT INTO tipos_empresa (nome, descricao, ativo) VALUES
('Cliente', 'Empresa que envia pallets', TRUE),
('Transportadora', 'Empresa responsável pelo transporte', TRUE),
('Destinatário', 'Empresa que recebe pallets', TRUE);

-- ============================================
-- TABELA: users
-- ============================================
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nome_completo VARCHAR(150) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    empresa_id INT,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABELA: empresas
-- ============================================
DROP TABLE IF EXISTS empresas;

CREATE TABLE empresas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    razao_social VARCHAR(200) NOT NULL,
    nome_fantasia VARCHAR(200),
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    inscricao_estadual VARCHAR(50),
    inscricao_municipal VARCHAR(50),
    tipo_empresa_id INT,
    cep VARCHAR(10),
    logradouro VARCHAR(200),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    telefone VARCHAR(20),
    celular VARCHAR(20),
    email VARCHAR(120),
    site VARCHAR(200),
    ativa BOOLEAN NOT NULL DEFAULT TRUE,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    criado_por_id INT NOT NULL,
    INDEX idx_cnpj (cnpj),
    INDEX idx_razao_social (razao_social),
    INDEX idx_ativa (ativa),
    INDEX idx_tipo_empresa (tipo_empresa_id),
    FOREIGN KEY (tipo_empresa_id) REFERENCES tipos_empresa(id),
    FOREIGN KEY (criado_por_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adicionar foreign key de empresa_id em users (após criar tabela empresas)
ALTER TABLE users 
ADD CONSTRAINT fk_users_empresa 
FOREIGN KEY (empresa_id) REFERENCES empresas(id);

-- ============================================
-- TABELA: motoristas
-- ============================================
DROP TABLE IF EXISTS motoristas;

CREATE TABLE motoristas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    placa_caminhao VARCHAR(10) NOT NULL,
    empresa_id INT NOT NULL,
    telefone VARCHAR(20),
    celular VARCHAR(20),
    email VARCHAR(120),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    cadastrado_por_id INT NOT NULL,
    INDEX idx_cpf (cpf),
    INDEX idx_nome (nome),
    INDEX idx_placa (placa_caminhao),
    INDEX idx_ativo (ativo),
    INDEX idx_empresa (empresa_id),
    FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    FOREIGN KEY (cadastrado_por_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABELA: vales_pallet
-- ============================================
DROP TABLE IF EXISTS vales_pallet;

CREATE TABLE vales_pallet (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    transportadora_id INT NOT NULL,
    destinatario_id INT NOT NULL,
    motorista_id INT,
    quantidade_pallets INT NOT NULL,
    numero_documento VARCHAR(100) NOT NULL,
    pin VARCHAR(4) NOT NULL UNIQUE,
    status VARCHAR(30) NOT NULL DEFAULT 'pendente_entrega',
    data_confirmacao DATETIME,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    criado_por_id INT NOT NULL,
    INDEX idx_pin (pin),
    INDEX idx_numero_documento (numero_documento),
    INDEX idx_status (status),
    INDEX idx_cliente (cliente_id),
    INDEX idx_transportadora (transportadora_id),
    INDEX idx_destinatario (destinatario_id),
    INDEX idx_motorista (motorista_id),
    INDEX idx_data_criacao (data_criacao),
    FOREIGN KEY (cliente_id) REFERENCES empresas(id),
    FOREIGN KEY (transportadora_id) REFERENCES empresas(id),
    FOREIGN KEY (destinatario_id) REFERENCES empresas(id),
    FOREIGN KEY (motorista_id) REFERENCES motoristas(id),
    FOREIGN KEY (criado_por_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABELA: logs_auditoria
-- ============================================
DROP TABLE IF EXISTS logs_auditoria;

CREATE TABLE logs_auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    modulo VARCHAR(100) NOT NULL,
    acao VARCHAR(50) NOT NULL,
    descricao TEXT NOT NULL,
    operacao_sql VARCHAR(20),
    tabela_afetada VARCHAR(100),
    registro_id INT,
    dados_anteriores TEXT,
    dados_novos TEXT,
    usuario_id INT,
    usuario_nome VARCHAR(150),
    ip_address VARCHAR(45),
    user_agent TEXT,
    sucesso BOOLEAN NOT NULL DEFAULT TRUE,
    mensagem_erro TEXT,
    tempo_execucao FLOAT,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_modulo (modulo),
    INDEX idx_acao (acao),
    INDEX idx_usuario (usuario_id),
    INDEX idx_data_hora (data_hora),
    INDEX idx_sucesso (sucesso),
    INDEX idx_tabela (tabela_afetada),
    FOREIGN KEY (usuario_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reabilitar verificações
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- VERIFICAÇÃO
-- ============================================
-- Listar tabelas criadas
SHOW TABLES;

-- Verificar estrutura de cada tabela
SELECT 
    TABLE_NAME as 'Tabela',
    TABLE_ROWS as 'Registros',
    ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) as 'Tamanho (MB)'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'epallet_db'
ORDER BY TABLE_NAME;

-- ============================================
-- MENSAGEM DE SUCESSO
-- ============================================
SELECT '============================================' as '';
SELECT 'ESTRUTURA DO BANCO CRIADA COM SUCESSO!' as 'STATUS';
SELECT '============================================' as '';
SELECT 'Próximos passos:' as '';
SELECT '1. Criar usuário administrador' as '';
SELECT '2. Configurar .env no Windows' as '';
SELECT '3. Executar aplicação Flask' as '';
SELECT '============================================' as '';
