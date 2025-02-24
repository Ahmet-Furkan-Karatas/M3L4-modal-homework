import discord
from discord.ext import commands
from discord import ui, ButtonStyle, TextStyle
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
        statuses = [x[0] for x in manager.get_statuses()]
        if self.project_status.value not in statuses:
            await interaction.response.send_message(
                "Seçtiğiniz durum geçersiz. Lütfen tekrar deneyin.", ephemeral=True
            )
            return

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

class UpdateProjectModal(ui.Modal, title="Proje Güncelle"):
    project_name = ui.TextInput(label="Güncellenecek Proje Adı", required=True)
    update_field = ui.TextInput(label="Güncellenecek Alan (Ad, Açıklama, Link, Durum)", required=True)
    new_value = ui.TextInput(label="Yeni Değer", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        projects = [x[2] for x in manager.get_projects(user_id)]
        if self.project_name.value not in projects:
            await interaction.response.send_message(
                "Bu projeye sahip değilsiniz, lütfen tekrar deneyin.", ephemeral=True
            )
            return

        attributes = {"Ad": "project_name", "Açıklama": "description", "Link": "url", "Durum": "status_id"}
        if self.update_field.value not in attributes:
            await interaction.response.send_message(
                "Geçersiz alan adı. Lütfen tekrar deneyin.", ephemeral=True
            )
            return

        if self.update_field.value == "Durum":
            statuses = manager.get_statuses()
            if self.new_value.value not in [x[0] for x in statuses]:
                await interaction.response.send_message("Yanlış durum seçildi, lütfen tekrar deneyin!", ephemeral=True)
                return
            update_value = manager.get_status_id(self.new_value.value)
        else:
            update_value = self.new_value.value

        manager.update_projects(attributes[self.update_field.value], (update_value, self.project_name.value, user_id))
        await interaction.response.send_message("Proje başarıyla güncellendi!")

class ProjectView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ui.Button(label="Başlat", style=ButtonStyle.green, custom_id="start"))
        self.add_item(ui.Button(label="Yeni Proje", style=ButtonStyle.blurple, custom_id="new_project"))
        self.add_item(ui.Button(label="Beceri Ekle", style=ButtonStyle.blurple, custom_id="skills"))
        self.add_item(ui.Button(label="Proje Sil", style=ButtonStyle.red, custom_id="delete"))
        self.add_item(ui.Button(label="Güncelle", style=ButtonStyle.gray, custom_id="update"))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.data["custom_id"] == "start":
            await interaction.response.send_modal(StartModal())
        elif interaction.data["custom_id"] == "new_project":
            await interaction.response.send_modal(NewProjectModal())
        elif interaction.data["custom_id"] == "skills":
            await interaction.response.send_modal(SkillsModal())
        elif interaction.data["custom_id"] == "delete":
            await interaction.response.send_modal(DeleteProjectModal())
        elif interaction.data["custom_id"] == "update":
            await interaction.response.send_modal(UpdateProjectModal())

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı")

@bot.command()
async def start(ctx):
    await ctx.send("Aşağıdaki butonları kullanarak işlemleri gerçekleştirebilirsiniz:", view=ProjectView())

bot.run(TOKEN)
