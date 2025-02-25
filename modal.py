import discord
from discord.ext import commands
from discord import ui, ButtonStyle
from config import TOKEN
from logic import DB_Manager
from config import DATABASE

manager = DB_Manager(DATABASE)

class StartModal(ui.Modal, title="Hoş Geldiniz!"):
    field_1 = ui.TextInput(label="Başlamak için herhangi bir mesaj yazın", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Merhaba! Ben bir proje yöneticisi botuyum.\nProjelerinizi ve onlara dair tüm bilgileri saklamanıza yardımcı olacağım! =)"
        )

class NewProjectModal(ui.Modal, title="Yeni Proje Ekle"):
    project_name = ui.TextInput(label="Proje Adı", required=True)
    project_link = ui.TextInput(label="Proje Bağlantısı", required=True)
    project_status = ui.TextInput(label="Proje Durumu", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        status_id = manager.get_status_id(self.project_status.value)
        data = [interaction.user.id, self.project_name.value, self.project_link.value, status_id]
        manager.insert_project([tuple(data)])
        await interaction.response.send_message("Proje başarıyla kaydedildi!")

class SkillsModal(ui.Modal, title="Proje Beceri Ekle"):
    project_name = ui.TextInput(label="Proje Adı", required=True)
    skill_name = ui.TextInput(label="Eklenecek Beceri", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        projects = [x[2] for x in manager.get_projects(user_id)]
        if self.project_name.value not in projects:
            await interaction.response.send_message(
                "Bu projeye sahip değilsiniz, lütfen tekrar deneyin.", ephemeral=True
            )
            return

        skills = [x[1] for x in manager.get_skills()]
        if self.skill_name.value not in skills:
            await interaction.response.send_message(
                "Geçersiz beceri, lütfen listeden seçin.", ephemeral=True
            )
            return

        manager.insert_skill(user_id, self.project_name.value, self.skill_name.value)
        await interaction.response.send_message(
            f"{self.skill_name.value} becerisi {self.project_name.value} projesine eklendi."
        )

class DeleteProjectModal(ui.Modal, title="Proje Sil"):
    project_name = ui.TextInput(label="Silmek İstediğiniz Proje Adı", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        projects = [x[2] for x in manager.get_projects(user_id)]
        if self.project_name.value not in projects:
            await interaction.response.send_message(
                "Bu projeye sahip değilsiniz, lütfen tekrar deneyin.", ephemeral=True
            )
            return

        project_id = manager.get_project_id(self.project_name.value, user_id)
        manager.delete_project(user_id, project_id)
        await interaction.response.send_message(f"{self.project_name.value} başarıyla silindi!")

class ShowProjectsModal(ui.Modal, title="Projelerinizi Görüntüle"):
    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        projects = manager.get_projects(user_id)
        
        if projects:
            text = "\n".join([f"Proje adı: {x[2]}\nBağlantı: {x[4]}\n" for x in projects])
            await interaction.response.send_message(text)
        else:
            await interaction.response.send_message('Henüz herhangi bir projeniz yok!')

class ProjectView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ui.Button(label="Yeni Proje Ekle", style=ButtonStyle.blurple, custom_id="new_project"))
        self.add_item(ui.Button(label="Projeleri Göster", style=ButtonStyle.blurple, custom_id="show_projects"))
        self.add_item(ui.Button(label="Beceri Ekle", style=ButtonStyle.blurple, custom_id="skills"))
        self.add_item(ui.Button(label="Proje Sil", style=ButtonStyle.red, custom_id="delete"))

    async def interaction_check(self, interaction: discord.Interaction):
        modal_classes = {
            "new_project": NewProjectModal,
            "skills": SkillsModal,
            "delete": DeleteProjectModal,
            "show_projects": ShowProjectsModal,
        }
        if interaction.data["custom_id"] in modal_classes:
            await interaction.response.send_modal(modal_classes[interaction.data["custom_id"]]())
