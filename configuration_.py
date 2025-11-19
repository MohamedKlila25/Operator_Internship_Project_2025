# Importation des modules nécessaires
import tkinter as tk                # Pour créer l'interface graphique
from tkinter import filedialog, messagebox, ttk  # Pour les dialogues de fichiers, messages et widgets stylés
import os                           # Pour gérer les fichiers et chemins
import uuid                         # Pour générer des identifiants uniques (requis pour l'artefact)

# Initialisation de la fenêtre principale
root = tk.Tk()                      # Crée la fenêtre principale de l'application
tech_var = tk.StringVar()           # Variable pour stocker la technologie sélectionnée (2G/3G, 4G, ou les trois)
entries = {}                        # Dictionnaire pour stocker les widgets de saisie (Entry)

# Fonction pour valider une adresse IP
def is_valid_ip(ip):
    """
    Vérifie si une adresse IP est valide (format xxx.xxx.xxx.xxx, chaque partie entre 0 et 255).
    Args:df_test={}
df_test['id']={'1','2','3'}
df_test["looks"]=["handsome","uply","repulsive"]
df_test['age']=[20,30,40]

        ip (str): Adresse IP à valider.
    Returns:
        bool: True si valide ou vide, False sinon.
    """
    if not ip:                      # Si le champ est vide, considéré comme valide (pour les champs optionnels)
        return True
    parts = ip.split('.')           # Sépare l'adresse IP en quatre parties
    if len(parts) != 4:             # Vérifie qu'il y a exactement quatre parties
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)  # Vérifie que chaque partie est un entier entre 0 et 255
    except ValueError:              # Gère les erreurs si une partie n'est pas un entier
        return False



# Fonction pour valider un VLAN ID
def is_valid_vlan(vlan):
    """
    Vérifie si un VLAN ID est valide (entier entre 1 et 4094).
    Args:
        vlan (str): VLAN ID à valider.
    Returns:
        bool: True si valide, False sinon.
    """
    try:
        vlan_id = int(vlan)         # Convertit la valeur en entier
        return 1 <= vlan_id <= 4094 # Vérifie que l'entier est entre 1 et 4094
    except ValueError:              # Gère les erreurs si la valeur n'est pas un entier
        return False

# Fonction pour effacer et activer/désactiver les champs
def update_fields(event):
    """
    Met à jour l'état des champs (activés/désactivés) et pré-remplit les valeurs par défaut
    en fonction de la technologie sélectionnée.
    Args:
        event: Événement déclenché par le changement de sélection dans la liste déroulante.
    """
    # Efface tous les champs et les active temporairement
    for field in entries:
        entries[field].delete(0, tk.END)  # Supprime le contenu actuel
        entries[field].config(state='normal')  # Active le champ (corrigé)

    techno = tech_var.get()  # Récupère la technologie sélectionnée
    if techno == "2G/3G":
        # Pré-remplit les champs 2G/3G avec des valeurs par défaut
        entries["port_number_2g3g"].insert(0, "7")
        entries["TG_transport"].insert(0, "TG63")
        # Désactive les champs 4G
        for field in fields_4g:
            entries[field].config(state='disabled')
    elif techno == "4G":
        # Pré-remplit les champs 4G avec des valeurs par défaut
        entries["port_number_4g"].insert(0, "6")
        entries["port_id"].insert(0, "TN_B")
        # Désactive les champs 2G/3G
        for field in fields_2g3g:
            entries[field].config(state='disabled')
    elif techno == "Les trois":
        # Pré-remplit les champs pour 2G/3G et 4G
        entries["port_number_2g3g"].insert(0, "7")
        entries["TG_transport"].insert(0, "TG63")
        entries["port_number_4g"].insert(0, "6")
        entries["port_id"].insert(0, "TN_B")
        # Tous les champs restent activés

# Fonction pour générer les scripts
def generate_script():
    """
    Génère les scripts de configuration pour 2G/3G, 4G, ou les deux, en fonction de la technologie sélectionnée.
    Valide les données saisies, génère le contenu des scripts, et les sauvegarde dans des fichiers texte.
    """
    techno = tech_var.get()  # Récupère la technologie sélectionnée
    if not techno:
        messagebox.showerror("Erreur", "Veuillez sélectionner une technologie !")
        return

    # Variables pour stocker les scripts générés
    scripts = []

    # Traitement pour 2G/3G (si 2G/3G ou Les trois est sélectionné)
    if techno in ["2G/3G", "Les trois"]:
        # Récupère les données saisies pour 2G/3G
        nom_station = entries["nom_station"].get()
        port_number = entries["port_number_2g3g"].get()
        iub_vlan = entries["IUB_vlan_number"].get()
        om_vlan = entries["OM_vlan_number"].get()
        abis_vlan = entries["ABIS_vlan_number"].get()
        siu_om_vlan = entries["SIU_OM_vlan_number"].get()
        abis_ip = entries["ABIS_primary_ip"].get()
        siu_om_ip = entries["SIU_OM_primary_ip"].get()
        tg_transport = entries["TG_transport"].get()
        
        # Validation des champs 2G/3G
        if not all([nom_station, port_number, iub_vlan, om_vlan, abis_vlan, siu_om_vlan, abis_ip, siu_om_ip, tg_transport]):
            messagebox.showerror("Erreur", "Tous les champs 2G/3G doivent être remplis !")
            return
        if not all(is_valid_vlan(v) for v in [iub_vlan, om_vlan, abis_vlan, siu_om_vlan]):
            messagebox.showerror("Erreur", "Les VLANs 2G/3G doivent être des entiers entre 1 et 4094 !")
            return
        if not all(is_valid_ip(ip) for ip in [abis_ip, siu_om_ip]):
            messagebox.showerror("Erreur", "Adresses IP 2G/3G invalides !")
            return
        try:
            port_number = int(port_number)  # Vérifie que port_number est un entier
        except ValueError:
            messagebox.showerror("Erreur", "Le numéro de port 2G/3G doit être un entier !")
            return

        # Génération du script 2G/3G
        script_content = "endtransaction t\n\nstarttransaction t\n\n"  # Début de la transaction
        script_content += "subscribe 172.31.42.8 1\n\n"  # Abonnement à l'adresse de gestion
        script_content += f"setmoattribute t stn=0 STN_Name {nom_station}\n"  # Définit le nom de la station
        script_content += f"setmoattribute t stn=0 promptprefix {nom_station}\n"  # Définit le préfixe du prompt
        script_content += "setmoattribute t stn=0 depip_interface STN=0,ipinterface=SIU_OM\n"  # Interface IP dépendante
        script_content += "setmoattribute t stn=0 STN_PGW_KeepalivePeriod 30\n"  # Période de keepalive
        script_content += "setmoattribute t stn=0 STN_PGW_L2TP_MaxTransmissions 10\n"  # Max transmissions L2TP
        script_content += "setmoattribute t stn=0 STN_PGW_L2TP_RetransmissionCap 4\n"  # Capacité de retransmission
        script_content += "setmoattribute t stn=0 systemclocktimeserver 192.168.13.133\n"  # Serveur NTP principal
        script_content += "setmoattribute t stn=0 wakeupdestination 172.31.42.8\n"  # Destination de réveil
        script_content += "setmoattribute t stn=0 wakeupeventinterval 2\n\n"  # Intervalle d'événement de réveil

        # Configuration de l'interface Ethernet RBS
        script_content += f"createmo t stn=0,EthernetInterface=RBS\n"
        script_content += f"setmoattribute t STN=0,EthernetInterface=RBS portnumber {port_number}\n"
        script_content += "setmoattribute t STN=0,EthernetInterface=RBS portId TN_A\n\n"
        # Configuration de l'interface Ethernet Metro
        script_content += "createmo t stn=0,EthernetInterface=Metro\n"
        script_content += "setmoattribute t STN=0,EthernetInterface=Metro port SFP\n"
        script_content += "setmoattribute t STN=0,EthernetInterface=Metro portnumber 1\n"
        script_content += "setmoattribute t STN=0,EthernetInterface=Metro portId TN_E\n\n"

        # Création des bridges pour Iub et OM
        script_content += "createmo t STN=0,bridge=Iub\n"
        script_content += "createmo t STN=0,bridge=OM\n\n"
        # Configuration du groupe VLAN pour RBS
        script_content += "createmo t STN=0,VLANGroup=RBS\n"
        script_content += "setmoattribute t STN=0,VLANGroup=RBS depLinkLayer STN=0,EthernetInterface=RBS\n"
        script_content += f"createmo t STN=0,VLANGroup=RBS,vlan=Iub\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=RBS,vlan=Iub depbridge STN=0,bridge=Iub\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=RBS,vlan=Iub tagvalue {iub_vlan}\n\n"
        script_content += f"createmo t STN=0,VLANGroup=RBS,vlan=OM\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=RBS,vlan=OM depbridge STN=0,bridge=OM\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=RBS,vlan=OM tagvalue {om_vlan}\n\n"
        # Configuration du groupe VLAN pour Metro
        script_content += "createmo t STN=0,VLANGroup=Metro\n"
        script_content += "setmoattribute t STN=0,VLANGroup=Metro depLinkLayer STN=0,EthernetInterface=Metro\n"
        script_content += f"createmo t STN=0,VLANGroup=Metro,vlan=Iub\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=Iub depbridge STN=0,bridge=Iub\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=Iub tagvalue {iub_vlan}\n\n"
        script_content += f"createmo t STN=0,VLANGroup=Metro,vlan=OM\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=OM depbridge STN=0,bridge=OM\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=OM tagvalue {om_vlan}\n\n"
        script_content += f"createmo t STN=0,VLANGroup=Metro,vlan=Abis\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=Abis tagvalue {abis_vlan}\n\n"
        script_content += f"createmo t STN=0,VLANGroup=Metro,vlan=SIU_OM\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=SIU_OM tagvalue {siu_om_vlan}\n\n"
        # Configuration de l'interface IP Abis
        script_content += "createmo t stn=0,ipinterface=Abis\n"
        script_content += f"setmoattribute t stn=0,ipinterface=Abis deplinklayer STN=0,VLANGroup=Metro,vlan=Abis\n"
        script_content += f"setmoattribute t stn=0,ipinterface=Abis primaryip_address {abis_ip}\n"
        script_content += "setmoattribute t stn=0,ipinterface=Abis primarysubnetmask 255.255.255.192\n\n"
        # Configuration de l'interface IP SIU_OM
        script_content += "createmo t stn=0,ipinterface=SIU_OM\n"
        script_content += f"setmoattribute t stn=0,ipinterface=SIU_OM deplinklayer STN=0,VLANGroup=Metro,vlan=SIU_OM\n"
        script_content += f"setmoattribute t stn=0,ipinterface=SIU_OM primaryip_address {siu_om_ip}\n"
        script_content += "setmoattribute t stn=0,ipinterface=SIU_OM primarysubnetmask 255.255.255.192\n"
        script_content += "setmoattribute t stn=0,ipinterface=SIU_OM defaultgateway 172.27.162.65\n\n"
        # Configuration des interfaces E1/T1
        script_content += "createmo t STN=0,e1t1interface=0\n"
        script_content += "createmo t STN=0,e1t1interface=1\n\n"
        # Configuration du TGTransport
        script_content += f"createmo t STN=0,tgtransport={tg_transport}\n"
        script_content += f"setmoattribute t STN=0,tgtransport={tg_transport} pgw_ip_address 172.31.54.131\n"
        script_content += f"setmoattribute t STN=0,tgtransport={tg_transport} depip_interface STN=0,ipinterface=Abis\n"
        script_content += f"setmoattribute t STN=0,tgtransport={tg_transport} overloadreportinterval 10\n"
        script_content += f"setmoattribute t STN=0,tgtransport={tg_transport} DSCP_L2TP_CP 51\n\n"
        script_content += f"createmo t stn=0,tgtransport={tg_transport},superchannel=0\n"
        script_content += f"createmo t stn=0,tgtransport={tg_transport},superchannel=1\n"
        script_content += f"setmoattribute t STN=0,tgtransport={tg_transport},superchannel=0 depe1t1interface 0\n"
        script_content += f"setmoattribute t STN=0,tgtransport={tg_transport},superchannel=1 depe1t1interface 1\n\n"
        # Configuration de la table de routage
        script_content += "createmo t stn=0,routingtable=0,iproute=Abis\n"
        script_content += f"setmoattribute t stn=0,routingtable=0,iproute=Abis admdistance 2\n"
        script_content += f"setmoattribute t stn=0,routingtable=0,iproute=Abis destipsubnet 172.31.54.128/26\n"
        script_content += f"setmoattribute t stn=0,routingtable=0,iproute=Abis forwardinginterface STN=0,ipinterface=Abis\n"
        script_content += f"setmoattribute t stn=0,routingtable=0,iproute=Abis nexthopipaddress 172.27.162.1\n\n"
        # Configuration des serveurs NTP
        script_content += "createmo t stn=0,synchronization=0,timeserver=NTP0\n"
        script_content += "setmoattribute t STN=0,Synchronization=0,TimeServer=NTP0 TS_IP_Address 192.168.14.138\n"
        script_content += f"setmoattribute t STN=0,Synchronization=0,TimeServer=NTP0 TS_priority 60\n"
        script_content += f"setmoattribute t stn=0,synchronization=0 synchType timeserver\n"
        script_content += f"setmoattribute t STN=0,Synchronization=0 depIP_Interface STN=0,IPInterface=SIU_OM\n\n"
        script_content += "createmo t stn=0,synchronization=0,timeserver=NTP1\n"
        script_content += f"setmoattribute t STN=0,Synchronization=0,TimeServer=NTP1 TS_IP_Address 192.168.10.25\n"
        script_content += f"setmoattribute t STN=0,Synchronization=0,TimeServer=NTP1 TS_priority 0\n"
        script_content += f"setmoattribute t stn=0,synchronization=0 synchType timeserver\n"
        script_content += f"setmoattribute t STN=0,Synchronization=0 depIP_Interface STN=0,IPInterface=SIU_OM\n\n"
        script_content += "createmo t stn=0,synchronization=0,timeserver=NTP2\n"
        script_content += f"setmoattribute t STN=0,Synchronization=0,TimeServer=NTP2 TS_IP_Address 192.168.13.133\n"
        script_content += f"setmoattribute t STN=0,Synchronization=0,TimeServer=NTP2 TS_priority 50\n"
        script_content += f"setmoattribute t stn=0,synchronization=0 synchType timeserver\n"
        script_content += f"setmoattribute t STN=0,Synchronization=0 depIP_Interface STN=0,IPInterface=SIU_OM\n\n"
        script_content += "commit t forcedcommit\n\n"  # Valide la transaction
        script_content += "endtransaction t\n"  # Fin de la transaction

        # Ajoute le script 2G/3G à la liste des scripts à sauvegarder
        scripts.append(("2G3G", script_content, f"siu_{nom_station}_2G3G.txt"))

    # Traitement pour 4G (si 4G ou Les trois est sélectionné)
    if techno in ["4G", "Les trois"]:
        # Récupère les données saisies pour 4G
        port_number = entries["port_number_4g"].get()
        port_id = entries["port_id"].get()
        s1_up_vlan = entries["vlan_s1_up"].get()
        s1_cp_vlan = entries["vlan_s1_cp"].get()
        enodeb_om_vlan = entries["vlan_enodeB_om"].get()

        # Validation des champs 4G
        if not all([port_number, port_id, s1_up_vlan, s1_cp_vlan, enodeb_om_vlan]):
            messagebox.showerror("Erreur", "Tous les champs 4G doivent être remplis !")
            return
        if not all(is_valid_vlan(v) for v in [s1_up_vlan, s1_cp_vlan, enodeb_om_vlan]):
            messagebox.showerror("Erreur", "Les VLANs 4G doivent être des entiers entre 1 et 4094 !")
            return
        try:
            port_number = int(port_number)  # Vérifie que port_number est un entier
        except ValueError:
            messagebox.showerror("Erreur", "Le numéro de port 4G doit être un entier !")
            return

        # Génération du script 4G
        script_content = "endtransaction t\n\nstarttransaction t\n\n"  # Début de la transaction
        # Configuration de l'interface Ethernet Enode_B
        script_content += f"createmo t stn=0,EthernetInterface=Enode_B\n"
        script_content += f"setmoattribute t STN=0,EthernetInterface=Enode_B portnumber {port_number}\n"
        script_content += f"setmoattribute t STN=0,EthernetInterface=Enode_B portId {port_id}\n\n"
        # Création des bridges pour 4G
        script_content += "createmo t STN=0,bridge=S1-UP\n"
        script_content += "createmo t STN=0,bridge=EnodeB_OM\n"
        script_content += "createmo t STN=0,bridge=S1-CP\n\n"
        # Configuration du groupe VLAN pour Enode_B
        script_content += "createmo t STN=0,VLANGroup=Enode_B\n"
        script_content += "setmoattribute t STN=0,VLANGroup=Enode_B depLinkLayer STN=0,EthernetInterface=Enode_B\n"
        script_content += f"createmo t STN=0,VLANGroup=Enode_B,vlan=S1-UP\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Enode_B,vlan=S1-UP depbridge STN=0,bridge=S1-UP\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Enode_B,vlan=S1-UP tagvalue {s1_up_vlan}\n\n"
        script_content += f"createmo t STN=0,VLANGroup=Enode_B,vlan=S1-CP\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Enode_B,vlan=S1-CP depbridge STN=0,bridge=S1-CP\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Enode_B,vlan=S1-CP tagvalue {s1_cp_vlan}\n\n"
        script_content += f"createmo t STN=0,VLANGroup=Enode_B,vlan=EnodeB_OM\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Enode_B,vlan=EnodeB_OM depbridge STN=0,bridge=EnodeB_OM\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Enode_B,vlan=EnodeB_OM tagvalue {enodeb_om_vlan}\n\n"
        # Configuration du groupe VLAN pour Metro
        script_content += "createmo t STN=0,VLANGroup=Metro\n"
        script_content += "setmoattribute t STN=0,VLANGroup=Metro depLinkLayer STN=0,EthernetInterface=Metro\n"
        script_content += f"createmo t STN=0,VLANGroup=Metro,vlan=S1-UP\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=S1-UP depbridge STN=0,bridge=S1-UP\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=S1-UP tagvalue {s1_up_vlan}\n\n"
        script_content += f"createmo t STN=0,VLANGroup=Metro,vlan=S1-CP\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=S1-CP depbridge STN=0,bridge=S1-CP\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=S1-CP tagvalue {s1_cp_vlan}\n\n"
        script_content += f"createmo t STN=0,VLANGroup=Metro,vlan=EnodeB_OM\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=EnodeB_OM depbridge STN=0,bridge=EnodeB_OM\n"
        script_content += f"setmoattribute t STN=0,VLANGroup=Metro,vlan=EnodeB_OM tagvalue {enodeb_om_vlan}\n\n"
        script_content += "checkconsistency t\n\n"  # Vérifie la cohérence
        script_content += "commit t\n"  # Valide le script

        # Ajoute le script 4G à la liste des scripts à sauvegarder
        scripts.append(("4G", script_content, "siu_lte_4G.txt"))

    # Sauvegarde des scripts
    for script_type, script_content, default_name in scripts:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt")],
            initialfile=default_name
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(script_content)  # Écrit le contenu dans le fichier
                messagebox.showinfo("Succès", f"Script {script_type} généré et sauvegardé !")
            except Exception as e:
                
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")

# Configuration de l'interface graphique
root.title("Générateur de Scripts 2G/3G/4G")  # Titre de la fenêtre
root.geometry("600x4000")  # Taille de la fenêtre (600x600 pixels)

main_frame = ttk.Frame(root, padding="100")  # Cadre principal pour organiser les widgets
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # Positionne le cadre

# Sélection de la technologie
ttk.Label(main_frame, text="Technologie :").grid(row=0, column=0, pady=10, sticky=tk.E)  # Étiquette pour la technologie
tech_menu = ttk.Combobox(main_frame, textvariable=tech_var, values=["2G/3G", "4G", "Les trois"], state="readonly")  # Liste déroulante
tech_menu.grid(row=0, column=1, pady=10, sticky=tk.W)  # Positionne la liste déroulante
tech_menu.bind("<<ComboboxSelected>>", update_fields)  # Associe la fonction update_fields au changement de sélection

# Champs pour 2G/3G
fields_2g3g = [
    "nom_station", "port_number_2g3g", "IUB_vlan_number", "OM_vlan_number",
    "ABIS_vlan_number", "SIU_OM_vlan_number", "ABIS_primary_ip",
    "SIU_OM_primary_ip", "TG_transport"
]
# Champs pour 4G
fields_4g = ["port_number_4g", "port_id", "vlan_s1_up", "vlan_s1_cp", "vlan_enodeB_om"]

# Création des champs de saisie
row = 1
# Ajoute une étiquette pour séparer les sections
ttk.Label(main_frame, text="Configuration 2G/3G", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=5)
row += 1
# Crée les champs pour 2G/3G
for field in fields_2g3g:
    ttk.Label(main_frame, text=field.replace("_", " ").title() + " :").grid(row=row, column=0, pady=5, sticky=tk.E)  # Étiquette pour le champ
    entry = ttk.Entry(main_frame)  # Champ de texte
    entry.grid(row=row, column=1, pady=5, sticky=tk.W)  # Positionne le champ
    entries[field] = entry  # Stocke le champ dans le dictionnaire
    row += 1

# Ajoute une étiquette pour la section 4G
ttk.Label(main_frame, text="Configuration 4G", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=5)
row += 1
# Crée les champs pour 4G
for field in fields_4g:
    ttk.Label(main_frame, text=field.replace("_", " ").title() + " :").grid(row=row, column=0, pady=5, sticky=tk.E)  # Étiquette pour le champ
    entry = ttk.Entry(main_frame)  # Champ de texte
    entry.grid(row=row, column=1, pady=5, sticky=tk.W)  # Positionne le champ
    entries[field] = entry  # Stocke le champ dans le dictionnaire
    row += 1

# Bouton pour générer le script
script_button = ttk.Button(main_frame, text="Générer Script", command=generate_script)  # Bouton pour lancer la génération
script_button.grid(row=row, column=0, columnspan=2, pady=20)  # Positionne le bouton

# Lancer l'application
root.mainloop()  # Démarre la boucle principale de l'interface graphique
