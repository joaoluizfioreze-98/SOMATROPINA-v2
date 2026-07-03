
import tkinter as tk
from tkinter import ttk, messagebox
import math

class GHRenovacao:
    def __init__(self, root):
        self.root = root
        root.title('GH - Renovação')
        root.geometry('950x700')

        self.classe = tk.StringVar(value='Crianca CID E23')
        self.conc_last = tk.StringVar(value='12')
        self.conc_curr = tk.StringVar(value='12')

        topo = ttk.LabelFrame(root, text='Dados da Renovação')
        topo.pack(fill='x', padx=10, pady=5)

        ttk.Label(topo, text='Classificação').grid(row=0, column=0, padx=5)
        ttk.Combobox(
            topo,
            textvariable=self.classe,
            values=['Crianca CID E23', 'Adulto CID E23', 'Crianca CID Q96', 'Adulto CID Q96'],
            width=25
        ).grid(row=0, column=1)

        ult = ttk.LabelFrame(root, text='Última dose deferida')
        ult.pack(fill='x', padx=10, pady=5)

        self.last_val = tk.Entry(ult, width=15)
        self.last_val.grid(row=0, column=0, padx=5, pady=5)

        self.last_unit = tk.StringVar(value='UI')
        ttk.Combobox(ult, textvariable=self.last_unit, values=['UI', 'mL'], width=8).grid(row=0, column=1)

        ttk.Label(ult, text='Aplicações/semana').grid(row=0, column=2, padx=5)
        self.last_days = ttk.Combobox(ult, values=['1','2','3','4','5','6','7'], width=5)
        self.last_days.set('7')
        self.last_days.grid(row=0, column=3)

        ttk.Label(ult, text='Concentração').grid(row=0, column=4, padx=5)
        ttk.Combobox(ult, textvariable=self.conc_last, values=['4','12'], width=8).grid(row=0, column=5)

        atual = ttk.LabelFrame(root, text='Dose atual')
        atual.pack(fill='x', padx=10, pady=5)

        self.curr_val = tk.Entry(atual, width=15)
        self.curr_val.grid(row=0, column=0, padx=5, pady=5)

        self.curr_unit = tk.StringVar(value='UI')
        u = ttk.Combobox(atual, textvariable=self.curr_unit, values=['UI','mL'], width=8)
        u.grid(row=0, column=1)

        ttk.Label(atual, text='Aplicações/semana').grid(row=0, column=2, padx=5)
        self.curr_days = ttk.Combobox(atual, values=['1','2','3','4','5','6','7'], width=5)
        self.curr_days.set('7')
        self.curr_days.grid(row=0, column=3)

        ttk.Label(atual, text='Concentração').grid(row=0, column=4, padx=5)
        ttk.Combobox(atual, textvariable=self.conc_curr, values=['4','12'], width=8).grid(row=0, column=5)

        self.conv = ttk.Label(atual, text='Equivalente: -')
        self.conv.grid(row=0, column=6, padx=10)

        self.curr_val.bind('<KeyRelease>', lambda e: self.update_equiv())
        u.bind('<<ComboboxSelected>>', lambda e: self.update_equiv())

        peso_box = ttk.LabelFrame(root, text='Peso (somente quando aplicável)')
        peso_box.pack(fill='x', padx=10, pady=5)

        self.peso = tk.Entry(peso_box, width=15)
        self.peso.pack(padx=5, pady=5)

        ttk.Button(root, text='Calcular Renovação', command=self.calcular).pack(pady=10)

        self.resultado = tk.Text(root, height=22)
        self.resultado.pack(fill='both', expand=True, padx=10, pady=5)

    def update_equiv(self):
        try:
            valor = float(self.curr_val.get().replace(',', '.'))
            conc = float(self.conc_curr.get())

            if self.curr_unit.get() == 'UI':
                self.conv.config(text=f'Equivalente: {valor/conc:.3f} mL')
            else:
                self.conv.config(text=f'Equivalente: {valor*conc:.3f} UI')
        except:
            self.conv.config(text='Equivalente: -')

    def calcular(self):
        try:
            classe = self.classe.get()

            peso_obrigatorio = classe in [
                'Crianca CID E23',
                'Crianca CID Q96',
                'Adulto CID Q96'
            ]

            if peso_obrigatorio and not self.peso.get().strip():
                messagebox.showwarning(
                    'Peso obrigatório',
                    'É necessário informar o peso para esta classificação.'
                )
                return

            conc_last = float(self.conc_last.get())
            conc_curr = float(self.conc_curr.get())

            lv = float(self.last_val.get().replace(',', '.'))
            cv = float(self.curr_val.get().replace(',', '.'))
            ld = float(self.last_days.get())
            cd = float(self.curr_days.get())

            last_ui = lv if self.last_unit.get() == 'UI' else lv * conc_last
            curr_ui = cv if self.curr_unit.get() == 'UI' else cv * conc_curr

            last_sem = last_ui * ld
            curr_sem = curr_ui * cd

            dose_confere = abs(last_sem - curr_sem) < 0.0001

            alertas = []
            limite_txt = 'Não aplicável'

            dose_dia = curr_sem / 7

            if classe == 'Crianca CID E23':
                peso = float(self.peso.get().replace(',', '.'))
                limite = 0.1 * peso
                limite_txt = f'{limite:.2f} UI/dia'
                if dose_dia > limite:
                    alertas.append('Dose acima do limite: 0,1 UI/kg/dia (Criança E23).')

            elif classe == 'Adulto CID E23':
                limite = 1
                limite_txt = '1,00 UI/dia'
                if dose_dia > limite:
                    alertas.append('Dose acima do limite: 1 UI/dia (Adulto E23).')

            else:
                peso = float(self.peso.get().replace(',', '.'))
                limite = 0.15 * peso
                limite_txt = f'{limite:.2f} UI/dia'
                if dose_dia > limite:
                    alertas.append('Dose acima do limite: 0,15 UI/kg/dia (Q96).')
                    alertas.append('A dose 0,2 UI/kg/dia somente casos especiais conforme PCDT, gentileza verificar.')

            ml_aplicacao = curr_ui / conc_curr
            frascos = math.ceil(ml_aplicacao * (cd / 7) * 30)

            if conc_curr == 4 and frascos > 93:
                alertas.append('Ultrapassa o limite de 93 frascos para 4 UI/mL.')

            if conc_curr == 12 and frascos > 31:
                alertas.append('Ultrapassa o limite de 31 frascos para 12 UI/mL.')

            self.resultado.delete('1.0', 'end')

            self.resultado.insert('end', 'RESUMO DA RENOVAÇÃO\n')
            self.resultado.insert('end', '-' * 40 + '\n')
            self.resultado.insert('end', f'Classificação: {classe}\n')
            self.resultado.insert('end', f'Dose deferida convertida: {last_ui:.2f} UI\n')
            self.resultado.insert('end', f'Dose atual convertida: {curr_ui:.2f} UI\n')
            self.resultado.insert('end', f'Dose máxima permitida: {limite_txt}\n')
            self.resultado.insert('end', f'Dose média diária: {dose_dia:.2f} UI/dia\n')
            self.resultado.insert('end', f'Frascos para 30 dias: {frascos}\n\n')

            if dose_confere:
                self.resultado.insert('end', '✅ Quantidade total de UI mantida entre a dose deferida e a atual.\n\n')
            else:
                self.resultado.insert('end', '⚠ Quantidade total de UI alterada entre a dose deferida e a atual.\n\n')

            if alertas:
                self.resultado.insert('end', '⚠ ALERTAS\n')
                for a in alertas:
                    self.resultado.insert('end', '- ' + a + '\n')
            else:
                self.resultado.insert('end', '✅ APTO PARA DISPENSAÇÃO\nDose dentro dos limites cadastrados.')

        except Exception as e:
            messagebox.showerror('Erro', str(e))

root = tk.Tk()
GHRenovacao(root)
root.mainloop()
