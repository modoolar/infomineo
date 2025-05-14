# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import base64

from odoo import fields, models


class EBDSWizard(models.TransientModel):
    _name = "e_bds"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    file_import = fields.Binary(string="Import File")
    file_export = fields.Binary(string="E-BDS file", readonly=True)
    name = fields.Char("Filename", size=256, readonly=True)
    state = fields.Selection(
        selection=(("choose", "choose"), ("get", "get")), default="choose"
    )

    def generate(self):
        payslipModel = self.env["hr.payslip"]
        e_bds_sortant = self.env["e_bds.sortant"]

        e_bds_sortant_id = e_bds_sortant.search(
            [("date_from", "<=", self.date_to), ("date_to", ">=", self.date_from)]
        )

        file_content_decoded = base64.decodebytes(self.file_import).decode("utf-8")
        data = file_content_decoded.split("\n")
        output = ""

        l1 = data[0]
        l1 = "B%sB%s" % (l1[1:17], l1[18:])
        output += "%s\n" % l1

        l2 = data[1]
        l2 = "B%s" % l2[1:]
        num_affilie = l2[3:10]
        periode_dec = l2[10:16]
        Nom_fichier = "DS_%s_%s.txt" % (num_affilie, periode_dec)
        output += "%s\n" % l2

        nombre_salaries = 0
        total_matriculation = 0
        total_working_days = 0
        total_salaire_reel = 0
        total_N_SALAIRE_Plaf = 0
        total_S_CTR = 0
        for emp in data[2:-2]:
            (
                output,
                nombre_salaries,
                total_matriculation,
                total_working_days,
                total_salaire_reel,
                total_N_SALAIRE_Plaf,
                total_S_CTR,
            ) = self.get_employee_data_from_ssnid(
                emp,
                e_bds_sortant_id,
                output,
                nombre_salaries,
                total_matriculation,
                total_working_days,
                total_salaire_reel,
                total_N_SALAIRE_Plaf,
                total_S_CTR,
            )
        NT1 = "".rjust(42, "0")

        B03 = (
            "B03"
            + l2[3:16]
            + str(nombre_salaries).rjust(6, "0")
            + NT1
            + str(total_matriculation).rjust(15, "0")
            + "".rjust(12, "0")
            + str(total_working_days).rjust(6, "0")
            + str(total_salaire_reel).rjust(15, "0")
            + str(total_N_SALAIRE_Plaf).rjust(13, "0")
            + str(total_S_CTR).rjust(19, "0")
            + "".rjust(116)
        )
        output += B03 + "\n"
        # Entrants
        bultain_ids = payslipModel.search(
            [
                ("normal", "=", False),
                ("date_from", "<=", self.date_to),
                ("date_to", ">=", self.date_from),
            ]
        )
        N_Nbr_Salaries_entrants = 0
        N_T_Num_Imma_entrants = 0
        N_T_Jours_Declare_entrants = 0
        N_T_Salaire_Reel_entrants = 0
        N_T_Salaire_Plaf_entrants = 0
        N_T_Ctr_entrants = 0
        # for entrant in bultain_salaire.browse(cr,uid,bultain_ids,context):
        for entrant in bultain_ids:
            (
                entrant,
                output,
                l2,
                N_Nbr_Salaries_entrants,
                N_T_Num_Imma_entrants,
                N_T_Jours_Declare_entrants,
                N_T_Salaire_Reel_entrants,
                N_T_Salaire_Plaf_entrants,
                N_T_Ctr_entrants,
            ) = self.get_employee_data_normal(
                entrant,
                output,
                l2,
                N_Nbr_Salaries_entrants,
                N_T_Num_Imma_entrants,
                N_T_Jours_Declare_entrants,
                N_T_Salaire_Reel_entrants,
                N_T_Salaire_Plaf_entrants,
                N_T_Ctr_entrants,
            )

        if not bultain_ids:
            salaire_entrant = (
                "B04"
                + l2[3:16]
                + str(0).rjust(9, "0")
                + str("").rjust(60)
                + str("").rjust(8, " ")
                + str(0).rjust(2, "0")
                + str(0).rjust(13, "0")
                + str(0).rjust(9, "0")
                + str(0).rjust(19, "0")
                + "".rjust(124)
            )
            output += salaire_entrant + "\n"

        B05 = (
            "B05"
            + l2[3:16]
            + str(N_Nbr_Salaries_entrants).rjust(6, "0")
            + str(N_T_Num_Imma_entrants).rjust(15, "0")
            + str(N_T_Jours_Declare_entrants).rjust(6, "0")
            + str(N_T_Salaire_Reel_entrants).rjust(15, "0")
            + str(N_T_Salaire_Plaf_entrants).rjust(13, "0")
            + str(N_T_Ctr_entrants).rjust(19, "0")
            + "".rjust(170)
        )
        output += B05 + "\n"

        N_Nbr_Salaries = nombre_salaries + N_Nbr_Salaries_entrants
        N_T_Num_Imma = total_matriculation + N_T_Num_Imma_entrants
        N_T_Jours_Declares = N_T_Jours_Declare_entrants + total_working_days
        N_T_Salaire_Reel = total_salaire_reel + N_T_Salaire_Reel_entrants
        N_T_Salaire_Plaf = N_T_Salaire_Plaf_entrants + total_N_SALAIRE_Plaf
        N_T_Ctr = total_S_CTR + N_T_Ctr_entrants
        B06 = (
            "B06"
            + l2[3:16]
            + str(N_Nbr_Salaries).rjust(6, "0")
            + str(N_T_Num_Imma).rjust(15, "0")
            + str(N_T_Jours_Declares).rjust(6, "0")
            + str(N_T_Salaire_Reel).rjust(15, "0")
            + str(N_T_Salaire_Plaf).rjust(13, "0")
            + str(N_T_Ctr).rjust(19, "0")
            + "".rjust(170)
        )
        output += B06 + "\n"
        out = base64.encodebytes(output.encode("utf-8"))
        self.state = "get"
        self.file_export = out
        self.name = Nom_fichier
        return {
            "type": "ir.actions.act_window",
            "res_model": "e_bds",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }

    def get_employee_data_from_ssnid(
        self,
        emp,
        e_bds_sortant_id,
        output,
        nombre_salaries,
        total_matriculation,
        total_working_days,
        total_salaire_reel,
        total_N_SALAIRE_Plaf,
        total_S_CTR,
    ):
        bultain_id = self.env["hr.payslip"].search(
            [
                ("employee_id.ssnid", "=", emp[16:25]),
                ("date_from", "<=", self.date_to),
                ("date_to", ">=", self.date_from),
            ]
        )

        if bultain_id:

            bultain_id[0].normal = True
            nombre_salaries += 1
            total_matriculation += int(emp[16:25])
            salaire_reel = bultain_id[0].gross_taxable_salary
            working_days = sum(
                line.number_of_days for line in bultain_id[0].worked_days_line_ids
            )
            total_working_days += int(working_days)

            salaire_reel_str = (
                str(int(salaire_reel * 100)).replace(".", "").rjust(13, "0")
            )
            total_salaire_reel += int(salaire_reel * 100)

            working_days = str(working_days)[:2].replace(".", "")
            N_AF_A_REVERSER = "".rjust(6, "0")
            if salaire_reel < 6000:
                sal_plaf = int(salaire_reel * 100)
            else:
                sal_plaf = 600000

            N_SALAIRE_Plaf = str(sal_plaf).replace(".", "").rjust(9, "0")
            total_N_SALAIRE_Plaf += int(sal_plaf)
            # Calcul de situation
            L_situation = ""
            situation_chiffre = 0

            if e_bds_sortant_id:
                e_bds_sortant_line_id = self.env["e_bds.sortant.line"].search(
                    [
                        ("e_bds_sortant_id", "=", e_bds_sortant_id[0].id),
                        ("employee_id.ssnid", "=", emp[16:25]),
                    ]
                )
                if e_bds_sortant_line_id:
                    L_situation = e_bds_sortant_line_id[0].situation
                    situation_chiffre = self.get_sortant_situation_code(L_situation)

            L_situation = L_situation.rjust(2)
            S_CTR = str(
                int(salaire_reel * 100)
                + int(emp[16:25])
                + int(N_SALAIRE_Plaf)
                + int(working_days)
                + situation_chiffre
            )

            total_S_CTR += int(S_CTR.replace(".", ""))

            L_filter = "".rjust(104)

            salaire_pre = (
                "B02"
                + emp[3:105]
                + N_AF_A_REVERSER
                + working_days.rjust(2, "0")
                + salaire_reel_str
                + N_SALAIRE_Plaf
                + L_situation
                + S_CTR.replace(".", "").rjust(19, "0")
                + L_filter
            )
            output += salaire_pre + "\n"
        # Sortants:
        else:
            if e_bds_sortant_id:
                e_bds_sortant_line_id = self.env["e_bds.sortant.line"].search(
                    [
                        ("e_bds_sortant_id", "=", e_bds_sortant_id[0].id),
                        ("employee_id.ssnid", "=", emp[16:25]),
                    ]
                )
                if e_bds_sortant_line_id:
                    nombre_salaries += 1
                    total_matriculation += int(emp[16:25])
                    situation = e_bds_sortant_line_id[0].situation
                    S_CTR_sortant = self.get_sortant_situation_code(situation)

                    S_CTR = str(int(emp[16:25]) + S_CTR_sortant)
                    total_S_CTR += int(S_CTR)
                    S_CTR_sortant = str(S_CTR).rjust(19, "0")

                    salaire_sortant = (
                        "B02"
                        + emp[3:105]
                        + "".rjust(30, "0")
                        + situation
                        + S_CTR_sortant
                        + "".rjust(104)
                    )
                    output += salaire_sortant + "\n"

        return (
            output,
            nombre_salaries,
            total_matriculation,
            total_working_days,
            total_salaire_reel,
            total_N_SALAIRE_Plaf,
            total_S_CTR,
        )

    def get_sortant_situation_code(self, situation):
        if situation == "SO":
            result = 1
        elif situation == "DE":
            result = 2
        elif situation == "IT":
            result = 3
        elif situation == "IL":
            result = 4
        elif situation == "AT":
            result = 5
        elif situation == "CS":
            result = 6
        elif situation == "MS":
            result = 7
        else:
            result = 8
        return result

    def get_employee_data_normal(
        self,
        entrant,
        output,
        l2,
        N_Nbr_Salaries_entrants,
        N_T_Num_Imma_entrants,
        N_T_Jours_Declare_entrants,
        N_T_Salaire_Reel_entrants,
        N_T_Salaire_Plaf_entrants,
        N_T_Ctr_entrants,
    ):
        N_Num_Assure = entrant.employee_id.ssnid
        L_Nom_Prenom = entrant.employee_id.name
        L_Num_CIN = entrant.employee_id.cin
        N_Nbr_Jours = int(
            str(
                sum(line.number_of_days for line in entrant.worked_days_line_ids)
            ).replace(".", "")[:-1]
        )
        N_Sal_Reel = int(entrant.gross_taxable_salary * 100)
        if N_Sal_Reel < 600000:
            N_Sal_Plaf = N_Sal_Reel
        else:
            N_Sal_Plaf = 600000

        if not N_Num_Assure:
            N_Num_Assure = "0"
        S_Ctr = int(N_Num_Assure) + N_Nbr_Jours + N_Sal_Reel + N_Sal_Plaf

        N_Nbr_Salaries_entrants += 1
        N_T_Num_Imma_entrants += int(N_Num_Assure)
        N_T_Jours_Declare_entrants += N_Nbr_Jours
        N_T_Salaire_Reel_entrants += N_Sal_Reel
        N_T_Salaire_Plaf_entrants += N_Sal_Plaf
        N_T_Ctr_entrants += S_Ctr

        salaire_entrant = (
            "B04"
            + l2[3:16]
            + str(N_Num_Assure).rjust(9, "0")
            + str(L_Nom_Prenom).rjust(60)
            + str(L_Num_CIN).rjust(8, " ")
            + str(N_Nbr_Jours).rjust(2, "0")
            + str(N_Sal_Reel).rjust(13, "0")
            + str(N_Sal_Plaf).rjust(9, "0")
            + str(S_Ctr).rjust(19, "0")
            + "".rjust(124)
        )
        output += salaire_entrant + "\n"

        return (
            entrant,
            output,
            l2,
            N_Nbr_Salaries_entrants,
            N_T_Num_Imma_entrants,
            N_T_Jours_Declare_entrants,
            N_T_Salaire_Reel_entrants,
            N_T_Salaire_Plaf_entrants,
            N_T_Ctr_entrants,
        )
