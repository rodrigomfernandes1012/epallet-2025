"""
Script de migração para adicionar sistema de perfis e permissões
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Perfil, PerfilPermissao, User

# Módulos do sistema
MODULOS_SISTEMA = [
    'dashboard',
    'empresas',
    'tipos_empresa',
    'motoristas',
    'vale_pallet',
    'relatorios',
    'logs',
    'usuarios',
    'perfis',
]


def criar_perfil(nome, descricao, permissoes_config, sistema=True):
    """
    Cria um perfil com suas permissões
    
    Args:
        nome: Nome do perfil
        descricao: Descrição do perfil
        permissoes_config: Dict com configuração de permissões por módulo
        sistema: Se é perfil do sistema (não pode ser excluído)
    
    Exemplo de permissoes_config:
    {
        'dashboard': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
        'empresas': {'visualizar': True, 'criar': True, 'editar': True, 'excluir': True},
    }
    """
    # Verificar se perfil já existe
    perfil = Perfil.query.filter_by(nome=nome).first()
    if perfil:
        print(f"  ⚠️  Perfil '{nome}' já existe. Pulando...")
        return perfil
    
    # Criar perfil
    perfil = Perfil(
        nome=nome,
        descricao=descricao,
        ativo=True,
        sistema=sistema
    )
    db.session.add(perfil)
    db.session.flush()  # Para obter o ID
    
    print(f"  ✅ Perfil '{nome}' criado com sucesso!")
    
    # Criar permissões
    for modulo in MODULOS_SISTEMA:
        config = permissoes_config.get(modulo, {
            'visualizar': False,
            'criar': False,
            'editar': False,
            'excluir': False
        })
        
        permissao = PerfilPermissao(
            perfil_id=perfil.id,
            modulo=modulo,
            pode_visualizar=config.get('visualizar', False),
            pode_criar=config.get('criar', False),
            pode_editar=config.get('editar', False),
            pode_excluir=config.get('excluir', False)
        )
        db.session.add(permissao)
    
    print(f"  ✅ Permissões criadas para '{nome}'")
    
    return perfil


def migrar():
    """Executa a migração"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("MIGRAÇÃO: Sistema de Perfis e Permissões")
        print("="*60 + "\n")
        
        # 1. Criar tabelas
        print("1️⃣  Criando tabelas...")
        db.create_all()
        print("  ✅ Tabelas criadas!\n")
        
        # 2. Criar perfis padrão
        print("2️⃣  Criando perfis padrão...\n")
        
        # Perfil: Administrador (acesso total)
        print("📋 Criando perfil: Administrador")
        admin_config = {}
        for modulo in MODULOS_SISTEMA:
            admin_config[modulo] = {
                'visualizar': True,
                'criar': True,
                'editar': True,
                'excluir': True
            }
        
        perfil_admin = criar_perfil(
            nome='Administrador',
            descricao='Acesso total ao sistema. Pode gerenciar usuários, perfis e todas as funcionalidades.',
            permissoes_config=admin_config,
            sistema=True
        )
        print()
        
        # Perfil: Gestor (acesso completo exceto admin)
        print("📋 Criando perfil: Gestor")
        gestor_config = {}
        for modulo in MODULOS_SISTEMA:
            if modulo in ['usuarios', 'perfis']:
                # Gestor não pode gerenciar usuários e perfis
                gestor_config[modulo] = {
                    'visualizar': False,
                    'criar': False,
                    'editar': False,
                    'excluir': False
                }
            else:
                # Acesso total aos demais módulos
                gestor_config[modulo] = {
                    'visualizar': True,
                    'criar': True,
                    'editar': True,
                    'excluir': True
                }
        
        perfil_gestor = criar_perfil(
            nome='Gestor',
            descricao='Acesso completo aos módulos operacionais. Pode gerenciar empresas, motoristas e vales.',
            permissoes_config=gestor_config,
            sistema=True
        )
        print()
        
        # Perfil: Operador (acesso limitado)
        print("📋 Criando perfil: Operador")
        operador_config = {
            'dashboard': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
            'empresas': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
            'tipos_empresa': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
            'motoristas': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
            'vale_pallet': {'visualizar': True, 'criar': True, 'editar': True, 'excluir': False},
            'relatorios': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
            'logs': {'visualizar': False, 'criar': False, 'editar': False, 'excluir': False},
            'usuarios': {'visualizar': False, 'criar': False, 'editar': False, 'excluir': False},
            'perfis': {'visualizar': False, 'criar': False, 'editar': False, 'excluir': False},
        }
        
        perfil_operador = criar_perfil(
            nome='Operador',
            descricao='Acesso operacional. Pode criar e editar vales pallet, visualizar empresas e motoristas.',
            permissoes_config=operador_config,
            sistema=True
        )
        print()
        
        # Perfil: Consulta (apenas visualização)
        print("📋 Criando perfil: Consulta")
        consulta_config = {
            'dashboard': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
            'empresas': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
            'tipos_empresa': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
            'motoristas': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
            'vale_pallet': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
            'relatorios': {'visualizar': True, 'criar': False, 'editar': False, 'excluir': False},
            'logs': {'visualizar': False, 'criar': False, 'editar': False, 'excluir': False},
            'usuarios': {'visualizar': False, 'criar': False, 'editar': False, 'excluir': False},
            'perfis': {'visualizar': False, 'criar': False, 'editar': False, 'excluir': False},
        }
        
        perfil_consulta = criar_perfil(
            nome='Consulta',
            descricao='Acesso somente leitura. Pode visualizar informações mas não pode criar ou editar.',
            permissoes_config=consulta_config,
            sistema=True
        )
        print()
        
        # 3. Atribuir perfil Administrador aos usuários existentes
        print("3️⃣  Atribuindo perfil aos usuários existentes...\n")
        
        usuarios_sem_perfil = User.query.filter_by(perfil_id=None).all()
        
        if usuarios_sem_perfil:
            for usuario in usuarios_sem_perfil:
                usuario.perfil_id = perfil_admin.id
                print(f"  ✅ Usuário '{usuario.username}' → Perfil 'Administrador'")
            
            db.session.commit()
            print(f"\n  ✅ {len(usuarios_sem_perfil)} usuário(s) atualizado(s)!")
        else:
            print("  ℹ️  Nenhum usuário sem perfil encontrado.")
        
        print()
        
        # 4. Commit final
        print("4️⃣  Salvando alterações...")
        db.session.commit()
        print("  ✅ Migração concluída com sucesso!\n")
        
        # Resumo
        print("="*60)
        print("RESUMO DA MIGRAÇÃO")
        print("="*60)
        print(f"✅ Perfis criados: 4")
        print(f"   - Administrador (acesso total)")
        print(f"   - Gestor (acesso operacional completo)")
        print(f"   - Operador (acesso limitado)")
        print(f"   - Consulta (somente leitura)")
        print()
        print(f"✅ Permissões criadas: {len(MODULOS_SISTEMA) * 4}")
        print()
        print(f"✅ Usuários atualizados: {len(usuarios_sem_perfil)}")
        print()
        print("="*60)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60 + "\n")


if __name__ == '__main__':
    try:
        migrar()
    except Exception as e:
        print(f"\n❌ ERRO na migração: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
