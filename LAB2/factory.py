from datetime import datetime
import xml.etree.ElementTree as ET
import player_pb2
from player import Player
from collections import defaultdict


class PlayerFactory:
    def to_json(self, players):
        '''
            This function should transform a list of Player objects into a list with dictionaries.
        '''
        lst = []
        res = {}
        for player in players:
            res["nickname"] = player.nickname
            res["email"] = player.email
            res["date_of_birth"] = player.date_of_birth.strftime("%Y-%m-%d")
            res["xp"] = player.xp
            res["class"] = player.cls
            lst.append(res)
            res = {}
        return lst

    def from_json(self, list_of_dict):
        '''
            This function should transform a list of dictionaries into a list with Player objects.
        '''

        return [Player(d['nickname'], d['email'], d['date_of_birth'], d['xp'], d['class']) for d in list_of_dict]

    def from_xml(self, xml_string):
        '''
            This function should transform a XML string into a list with Player objects.
        '''
        players = []

        root = ET.fromstring(xml_string)

        for player_elem in root.findall(".//player"):
            nickname = player_elem.find("nickname").text
            email = player_elem.find("email").text
            date_of_birth = player_elem.find("date_of_birth").text
            xp = int(player_elem.find('xp').text)
            cls = player_elem.find('class').text
            player = Player(nickname, email, date_of_birth, xp, cls)
            players.append(player)

        return players


    def to_xml(self, list_of_players):
        '''
            This function should transform a list with Player objects into a XML string.
        '''
        root = ET.Element("data")

        for player in list_of_players:
            player_element = ET.SubElement(root, "player")
            nickname = ET.SubElement(player_element, "nickname")
            nickname.text = player.nickname
            email = ET.SubElement(player_element, "email")
            email.text = player.email
            date_of_birth = ET.SubElement(player_element, "date_of_birth")
            date_of_birth.text = datetime.strftime(player.date_of_birth, "%Y-%m-%d")
            xp = ET.SubElement(player_element, "xp")
            xp.text = str(player.xp)
            cls = ET.SubElement(player_element, "class")
            cls.text = player.cls

        return ET.tostring(root, encoding="utf-8")

    def from_protobuf(self, binary):
        '''
            This function should transform a binary protobuf string into a list with Player objects.
        '''
        player_list = player_pb2.PlayersList()
        player_list.ParseFromString(binary)
        classes = ['Berserk', 'Tank', 'Paladin', 'Mage']
        players = []
        for pb_player in player_list.player:
            player = Player(pb_player.nickname, pb_player.email, pb_player.date_of_birth, pb_player.xp, classes[pb_player.cls])
            players.append(player)

        return players

    def to_protobuf(self, list_of_players):
        '''
            This function should transform a list with Player objects into a binary protobuf string.
        '''

        player_list = player_pb2.PlayersList()
        for player in list_of_players:
            pb_player = player_list.player.add()
            pb_player.nickname = player.nickname
            pb_player.email = player.email
            pb_player.date_of_birth = player.date_of_birth.strftime("%Y-%m-%d")
            pb_player.xp = player.xp
            pb_player.cls = player.cls

        return player_list.SerializeToString()