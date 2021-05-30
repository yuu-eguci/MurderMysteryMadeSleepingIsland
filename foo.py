"""
マーダーミステリー「魔法使いの眠る島」、黒のコード所有者特定プログラム。

1ターン目終了時のドローンの
- HP
- 場所
- 所持アイテム
を入力すると、こんな結果を返す想定。

***
パターン解析結果(実行されたコードの順番)
赤 -> 青 -> 紫 -> 黒赤
青 -> 青黒 -> 紫 -> 赤
***
確定コード
3人目は紫コードの持ち主です。
"""

from pprint import pprint
from enum import Enum, auto
import itertools


class Location(Enum):
    # Drone の居場所を表す enum です。
    INITIAL = auto()
    RED = auto()
    BLUE = auto()
    GREEN = auto()
    PURPLE = auto()


ITEM = {
    Location.RED: 'RED',
    Location.BLUE: 'BLUE',
    Location.GREEN: 'GREEN',
    Location.PURPLE: 'PURPLE',
}


class Drone:
    # ドローンのクラスです。

    def __init__(self, hp=3, location=Location.INITIAL, inventory=None):
        self.hp = hp
        self.location = location
        self.inventory = inventory if inventory else []

    def __repr__(self):
        return f'Drone(hp={self.hp}, location={self.location}, inventory={self.inventory})'


class Field:
    # 本ゲームのフィールドのクラスです。

    def __init__(self, red_item_left=4, blue_item_left=3, green_item_left=2, purple_item_left=3):
        # 各地域に残存するアイテムの個数を意味します。
        self.item_left = {
            Location.RED: red_item_left,
            Location.BLUE: blue_item_left,
            Location.GREEN: green_item_left,
            Location.PURPLE: purple_item_left,
        }

    def __repr__(self):
        return (
            f'Field(red_item_left={self.item_left[Location.RED]},'
            f' blue_item_left={self.item_left[Location.BLUE]},'
            f' green_item_left={self.item_left[Location.GREEN]},'
            f' purple_item_left={self.item_left[Location.PURPLE]})'
        )


class Code:
    # プレイヤーが選択できるコードです。すべてのコードはゲーム情報である Fields, Drone インスタンスの依存性注入を受けます。

    @classmethod
    def red(cls, field, drone, previous_code_name='', next_code_name=''):
        drone.location = Location.RED
        drone.inventory.append(ITEM[Location.RED])
        field.item_left[Location.RED] -= 1

    @classmethod
    def blue(cls, field, drone, previous_code_name='', next_code_name=''):
        drone.location = Location.BLUE
        drone.inventory.append(ITEM[Location.BLUE])
        field.item_left[Location.BLUE] -= 1

    @classmethod
    def green(cls, field, drone, previous_code_name='', next_code_name=''):
        drone.location = Location.GREEN
        drone.inventory.append(ITEM[Location.GREEN])
        field.item_left[Location.GREEN] -= 1

    @classmethod
    def purple(cls, field, drone, previous_code_name='', next_code_name=''):
        drone.location = Location.PURPLE
        drone.inventory.append(ITEM[Location.PURPLE])
        field.item_left[Location.PURPLE] -= 1

    @classmethod
    def white(cls, field, drone, previous_code_name='', next_code_name=''):
        if previous_code_name.startswith('black'):
            # 黒の無効化は、黒 code 側で行います。
            pass
            # drone の現在地のアイテムを3つまで取得。3つ残っていない場合もあることに注意。
            for i in range(3):
                # アイテム取得は Location.INITIAL では不可。
                if drone.location == Location.INITIAL:
                    break

                if field.item_left[drone.location] < 0:
                    break
                field.item_left[drone.location] -= 1
                drone.inventory.append(ITEM[drone.location])
            return

        drone.hp -= 1

    @classmethod
    def black(cls, field, drone, previous_code_name='', next_code_name=''):
        if next_code_name == 'white':
            return
        drone.hp -= 1

    @classmethod
    def black_red(cls, field, drone, previous_code_name='', next_code_name=''):
        if next_code_name == 'white':
            return
        if drone.location == Location.RED:
            drone.hp -= 3

    @classmethod
    def black_blue(cls, field, drone, previous_code_name='', next_code_name=''):
        if next_code_name == 'white':
            return
        if drone.location == Location.BLUE:
            drone.hp -= 3

    @classmethod
    def black_green(cls, field, drone, previous_code_name='', next_code_name=''):
        if next_code_name == 'white':
            return
        if drone.location == Location.GREEN:
            drone.hp -= 3

    @classmethod
    def black_purple(cls, field, drone, previous_code_name='', next_code_name=''):
        if next_code_name == 'white':
            return
        if drone.location == Location.PURPLE:
            drone.hp -= 3


def create_all_code_patterns_generator():
    # 4人のプレイヤーにより入力されるコードのパターンをすべて網羅します。
    # 返却値は [code, code, code, code] の配列で、配列の順番がコード入力の順番となります。

    PURPLE_PLAYER_CODES = [
        Code.red,
        Code.blue,
        Code.green,
        Code.purple,
    ]
    RAINBOW_PLAYER_CODES = [
        Code.red,
        Code.blue,
        Code.green,
        Code.purple,
        Code.white,
        Code.black,
        Code.black_red,
        Code.black_blue,
        Code.black_green,
        Code.black_purple,
    ]
    WHITE_PLAYER_CODES = [
        Code.red,
        Code.blue,
        Code.green,
        Code.white,
    ]
    BLACK_PLAYER_CODES = [
        Code.black,
        Code.black_red,
        Code.black_blue,
        Code.black_green,
        Code.black_purple,
    ]

    # 4人のプレイヤーの code 入力順序全パターン。
    players = [PURPLE_PLAYER_CODES, RAINBOW_PLAYER_CODES, WHITE_PLAYER_CODES, BLACK_PLAYER_CODES]
    player_permutations = itertools.permutations(players, len(players))

    # この for では、 players の全順列が取得できます。
    # NOTE: 何このコードヤバすぎ。
    for player_codes_list in player_permutations:
        player_code1 = player_codes_list[0]
        player_code2 = player_codes_list[1]
        player_code3 = player_codes_list[2]
        player_code4 = player_codes_list[3]
        for code1 in player_code1:
            for code2 in player_code2:
                for code3 in player_code3:
                    for code4 in player_code4:
                        yield [code1, code2, code3, code4]


def run(hp, location, inventory, code_patterns=None):
    # メインの処理です。 hp, location, inventory の値から、何が起こったのか分析します。
    # inventory は list です。最終的に比較に使いますが、そのとき順番は不問です。
    # 順番を気にせず比較するため、あらかじめソートしておきます。
    sorted_inventory = sorted(inventory)

    # 今回の分析において可能性のある code_patterns です。
    # 与えられなければ、全可能性を用意します。(19,199通りの試算なので iterator で用意。)
    if code_patterns == None:
        code_patterns = create_all_code_patterns_generator()

    # 分析は次のように行います。
    # 1. 全可能性ぶん、ドローンを用意して、全可能性ぶんの結果を観測する。
    # 2. 与えられた値と合致するパターンが、今回起こったパターンです。
    #    もちろん複数パターンが算出されることもあるでしょう。
    possible_code_pattern = []
    for code_pattern in code_patterns:

        # 今回の code_pattern のための drone を生成します。
        drone = Drone()
        # 今回の code_pattern のための field を生成します。
        field = Field()

        # code_pattern はこんな感じになっています。順番に実行します。
        # [Code.***, Code.***, Code.***, Code.***]
        for i, code in enumerate(code_pattern):
            # コレの前の code name
            previous_code_name = '' if i == 0 else code_pattern[i - 1].__name__
            next_code_name = '' if i == 3 else code_pattern[i + 1].__name__
            code(
                field,
                drone,
                previous_code_name=previous_code_name,
                next_code_name=next_code_name,
            )

        # code_pattern のシミュレーションを終えた drone の状態が、
        # 与えられたものと一致した場合、今回の code_pattern こそが
        # 実際に発生した code_pattern である可能性があります。
        drone.inventory.sort()
        if hp == drone.hp and location == drone.location and sorted_inventory == drone.inventory:
            possible_code_pattern.append((
                code_pattern[0],
                code_pattern[1],
                code_pattern[2],
                code_pattern[3],
            ))

    return possible_code_pattern


if __name__ == '__main__':

    # 毎回 code func のリストを map __name__ かけて print してチェックするのが面倒なので関数化しています。
    def pprint_code_patterns(code_patterns):
        for _ in code_patterns:
            print(tuple(map(lambda x: x.__name__, _)))

    # 1st game の結果を入力してね。
    drone_after_first_game = Drone(
        hp=-1,
        location=Location.RED,
        inventory=[
            ITEM[Location.RED],
            ITEM[Location.PURPLE],
        ],
    )
    # こちらが 1st game で実行されたと考えられるコードの羅列。
    guesses_for_first_game = run(
        hp=drone_after_first_game.hp,
        location=drone_after_first_game.location,
        inventory=drone_after_first_game.inventory,
    )
    pprint_code_patterns(guesses_for_first_game)

    # 2nd game の結果を入力してね。
