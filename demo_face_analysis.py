#!/usr/bin/env python3
"""
Demonstração do Sistema Integrado de Análise Facial
Mostra como usar o sistema completo de reconhecimento facial e geração de contornos
"""

import os
import time
from python.face_contour_analyzer import FaceContourAnalyzer

def print_banner():
    """Imprime banner do sistema"""
    print("=" * 80)
    print("🎯 SISTEMA INTEGRADO DE ANÁLISE FACIAL - ANDROIDE VIRTUAL v2.1")
    print("🔬 Reconhecimento Facial + Geração de Contornos com MediaPipe + OpenCV")
    print("=" * 80)

def demo_complete_analysis():
    """Demonstração completa do sistema"""
    print("\n🚀 INICIANDO DEMONSTRAÇÃO COMPLETA...")
    
    # Inicializar analisador
    print("\n📦 Inicializando componentes...")
    analyzer = FaceContourAnalyzer()
    
    # Definir caminhos
    image_path = "assets/rosto3d.png"
    output_dir = "assets"
    
    print(f"\n📸 Imagem de entrada: {image_path}")
    print(f"📁 Diretório de saída: {output_dir}")
    
    # Verificar se a imagem existe
    if not os.path.exists(image_path):
        print(f"❌ Erro: Imagem não encontrada em {image_path}")
        return False
    
    # Executar análise completa
    print("\n🔍 Executando análise facial completa...")
    start_time = time.time()
    
    result = analyzer.process_image(image_path, output_dir)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    if "error" in result:
        print(f"❌ Erro durante processamento: {result['error']}")
        return False
    
    # Mostrar resultados detalhados
    print(f"\n✅ ANÁLISE CONCLUÍDA EM {processing_time:.2f} SEGUNDOS!")
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO DETALHADO DA ANÁLISE")
    print("=" * 60)
    
    print(f"🔢 Landmarks detectados: {result['landmarks_count']}")
    print(f"📅 Timestamp: {time.ctime(result['timestamp'])}")
    
    # Características dos olhos
    if 'eyes' in result['features']:
        eyes = result['features']['eyes']
        print(f"\n👁️ ANÁLISE DOS OLHOS:")
        print(f"   • Abertura esquerda: {eyes['left_openness']:.3f}")
        print(f"   • Abertura direita: {eyes['right_openness']:.3f}")
        print(f"   • Média de abertura: {eyes['average_openness']:.3f}")
        print(f"   • Estado: {'Piscando' if eyes['is_blinking'] else 'Abertos'}")
    
    # Características da boca
    if 'mouth' in result['features']:
        mouth = result['features']['mouth']
        print(f"\n👄 ANÁLISE DA BOCA:")
        print(f"   • Largura: {mouth['width']:.2f} pixels")
        print(f"   • Altura: {mouth['height']:.2f} pixels")
        print(f"   • Proporção: {mouth['aspect_ratio']:.3f}")
        print(f"   • Estado: {'Aberta' if mouth['is_open'] else 'Fechada'}")
    
    # Contornos detectados
    print(f"\n🎭 CONTORNOS DETECTADOS:")
    for region, points in result['contours'].items():
        if points:
            print(f"   • {region.replace('_', ' ').title()}: {len(points)} pontos")
    
    # Arquivos gerados
    print(f"\n📄 ARQUIVOS GERADOS ({len(result['files_generated'])}):")
    for file in result['files_generated']:
        file_path = os.path.join(output_dir, file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file} ({size:,} bytes)")
        else:
            print(f"   ❌ {file} (não encontrado)")
    
    return True

def demo_integration_info():
    """Mostra informações sobre integração com interface web"""
    print("\n" + "=" * 60)
    print("🌐 INTEGRAÇÃO COM INTERFACE WEB")
    print("=" * 60)
    
    print("\n📋 COMPONENTES INTEGRADOS:")
    print("   🐍 Python: face_contour_analyzer.py - Análise facial backend")
    print("   🌐 JavaScript: face-analysis.js - Interface web frontend")
    print("   🎨 CSS: face-analysis.css - Estilos visuais")
    print("   📄 HTML: index.html - Interface do usuário")
    
    print("\n🔄 FLUXO DE FUNCIONAMENTO:")
    print("   1. Usuário clica em 'ANALISAR IMAGEM' na interface web")
    print("   2. JavaScript carrega dados da análise Python existente")
    print("   3. Visualização dos contornos no canvas HTML5")
    print("   4. Geração automática de código de animação facial")
    print("   5. Atualização dos parâmetros faciais em tempo real")
    
    print("\n⚙️ RECURSOS DISPONÍVEIS:")
    print("   • Detecção de 478 landmarks faciais")
    print("   • Análise de olhos, boca, nariz e sobrancelhas")
    print("   • Geração de máscaras de contorno artísticas")
    print("   • Visualização interativa em canvas")
    print("   • Código JavaScript gerado automaticamente")
    print("   • Efeitos visuais em tempo real")

def main():
    """Função principal da demonstração"""
    print_banner()
    
    # Demonstração da análise completa
    success = demo_complete_analysis()
    
    if success:
        # Informações sobre integração
        demo_integration_info()
        
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
        print("\n📌 PRÓXIMOS PASSOS:")
        print("   1. Abra o arquivo index.html em um navegador")
        print("   2. Clique em 'INICIAR ANÁLISE COMPLETA'")
        print("   3. Explore os contornos gerados no canvas")
        print("   4. Veja o código JavaScript gerado automaticamente")
        print("   5. Experimente diferentes botões de análise")
        
        print("\n🔧 PERSONALIZAÇÃO:")
        print("   • Modifique face_contour_analyzer.py para novos algoritmos")
        print("   • Ajuste face-analysis.js para nova funcionalidade web")
        print("   • Customize face-analysis.css para visual diferente")
        
        print(f"\n📁 Todos os arquivos de saída estão em: assets/")
        print("   • rosto3d_mask_hull.png - Máscara convex hull")
        print("   • rosto3d_mask_outline.png - Contorno facial")
        print("   • rosto3d_mask_artistic.png - Máscara artística")
        print("   • rosto3d_debug.png - Imagem com landmarks")
        print("   • rosto3d_analysis.json - Dados da análise")
        
    else:
        print("\n❌ FALHA NA DEMONSTRAÇÃO")
        print("Verifique se:")
        print("   • A imagem assets/rosto3d.png existe")
        print("   • As dependências Python estão instaladas")
        print("   • MediaPipe e OpenCV estão funcionando")

if __name__ == "__main__":
    main()
