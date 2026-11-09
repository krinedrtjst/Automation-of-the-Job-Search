import json
from pathlib import Path
import re

def esc(text):
    text = str(text)
    chars = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
        '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in chars.keys()))
    return regex.sub(lambda match: chars[match.group(0)], text)

def carregar_dados():
    with open("privado/perfil_mestre.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def gerar_curriculo(dados, template_name, output_name):
    caminho_template = Path(f"templates/{template_name}.tex")
    caminho_saida = Path(f"{output_name}.tex")
    
    with open(caminho_template, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    conteudo = conteudo.replace('[[NAME]]', esc(dados['personal']['name']))
    conteudo = conteudo.replace('[[EMAIL]]', esc(dados['personal']['email']))
    conteudo = conteudo.replace('[[LOCATION]]', esc(dados['personal']['location']))
    conteudo = conteudo.replace('[[GITHUB]]', esc(dados['personal']['github']))
    conteudo = conteudo.replace('[[LINKEDIN]]', esc(dados['personal']['linkedin']))
    
    conteudo = conteudo.replace('[[SKILLS_AI]]', esc(', '.join(dados['skills']['data_ai'])))
    conteudo = conteudo.replace('[[SKILLS_BI]]', esc(', '.join(dados['skills']['bi_cloud'])))
    conteudo = conteudo.replace('[[SKILLS_PROG]]', esc(', '.join(dados['skills']['programming'])))

    exp_texto = ""
    for exp in dados['experience']:
        # Uses \textbar{} so ATS bots can read the separator
        exp_texto += f"\\noindent \\textbf{{{esc(exp['title'])}}} \\textbar{{}} {esc(exp['company'])} \\hfill {esc(exp['start_date'])} -- {esc(exp['end_date'])} \\par\n"
        # leftmargin=* forces bullets to align safely inside the page bounds
        exp_texto += "\\begin{itemize}[noitemsep,topsep=2pt,parsep=2pt,partopsep=0pt, leftmargin=*]\n"
        for bullet in exp['bullets']:
            exp_texto += f"    \\item {esc(bullet)}\n"
        exp_texto += "\\end{itemize}\n\\vspace{6pt}\n\n"
    conteudo = conteudo.replace('[[EXPERIENCE_BLOCK]]', exp_texto)

    edu_texto = ""
    for edu in dados['education']:
        # Splits Degree and Institution into two separate lines to prevent date wrapping
        edu_texto += f"\\noindent \\textbf{{{esc(edu['degree'])}}} \\hfill {esc(edu['start_date'])} -- {esc(edu['end_date'])} \\par\n"
        edu_texto += f"\\noindent \\textit{{{esc(edu['institution'])}}} \\par \\vspace{{6pt}}\n"
    conteudo = conteudo.replace('[[EDUCATION_BLOCK]]', edu_texto)
    
    proj_texto = ""
    for proj in dados['projects']:
        proj_texto += f"\\noindent \\textbf{{{esc(proj['name'])}}} \\textbar{{}} \\textit{{{esc(', '.join(proj['technologies']))}}} \\par\n"
        proj_texto += f"\\vspace{{2pt}} {esc(proj['description'])} \\par \\vspace{{6pt}}\n"
    conteudo = conteudo.replace('[[PROJECTS_BLOCK]]', proj_texto)

    with open(caminho_saida, 'w', encoding='utf-8') as f:
        f.write(conteudo)
        
    print(f"✅ Currículo LaTeX corrigido gerado com sucesso: {caminho_saida}")

if __name__ == "__main__":
    dados = carregar_dados()
    gerar_curriculo(dados, "base_data_science", "curriculo_gerado")
