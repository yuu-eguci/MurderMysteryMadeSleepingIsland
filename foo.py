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


class Player(Enum):
    # 実際のプレイヤーを表す enum です。
    # 名前は実際のゲームで使われている名称です。
    PYTHON = auto()
    TASK = auto()
    MONITOR = auto()
    DB = auto()


class PlayerCharacter(Enum):
    # Player の正体を表す enum です。
    PURPLE = auto()
    RAINBOW = auto()
    WHITE = auto()
    BLACK = auto()


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


# 各プレイヤーが利用できるコードの種類です。
PLAYER_AVAILABLE_CODES = {
    Player.PURPLE: [
        Code.red,
        Code.blue,
        Code.green,
        Code.purple,
    ],
    Player.RAINBOW: [
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
    ],
    Player.WHITE: [
        Code.red,
        Code.blue,
        Code.green,
        Code.white,
    ],
    Player.BLACK: [
        Code.black,
        Code.black_red,
        Code.black_blue,
        Code.black_green,
        Code.black_purple,
    ],
}


def create_code_patterns_generator(player_patterns):
    # 4人のプレイヤーにより入力されるコードのパターンをすべて網羅します。
    # 返却値は [code, code, code, code] の配列で、配列の順番がコード入力の順番となります。

    # この for では、 players の全順列が取得できます。
    # NOTE: 何このコードヤバすぎ。
    for player_pattern in player_patterns:
        player_codes1 = PLAYER_AVAILABLE_CODES[player_pattern[0]]
        player_codes2 = PLAYER_AVAILABLE_CODES[player_pattern[1]]
        player_codes3 = PLAYER_AVAILABLE_CODES[player_pattern[2]]
        player_codes4 = PLAYER_AVAILABLE_CODES[player_pattern[3]]
        for code1 in player_codes1:
            for code2 in player_codes2:
                for code3 in player_codes3:
                    for code4 in player_codes4:
                        yield {
                            'code_pattern': [code1, code2, code3, code4],
                            'player_pattern': player_pattern,
                        }


def run(hp, location, inventory, player_patterns=None):
    # メインの処理です。 hp, location, inventory の値から、何が起こったのか分析します。
    # inventory は list です。最終的に比較に使いますが、そのとき順番は不問です。
    # 順番を気にせず比較するため、あらかじめソートしておきます。
    sorted_inventory = sorted(inventory)

    # ありうるプレイヤーの順列リスト。これが length=1 ということになれば、全員の色が判明した、ということです。
    # 最初(None)はもちろん、全可能性がありるので、全パターン用意します。
    if player_patterns is None:
        players = [Player.PURPLE, Player.RAINBOW, Player.WHITE, Player.BLACK]
        player_patterns = itertools.permutations(players, len(players))

    # この player_patterns のときありうる code_patterns を取得します。
    # 最大で19,199通りの試算なので iterator で用意。
    patterns = create_code_patterns_generator(player_patterns)

    # 分析は次のように行います。
    # 1. 全可能性ぶん、ドローンを用意して、全可能性ぶんの結果を観測する。
    # 2. 与えられた値と合致するパターンが、今回起こったパターンです。
    #    もちろん複数パターンが算出されることもあるでしょう。
    possible_patterns = []
    for pattern in patterns:

        code_pattern = pattern['code_pattern']
        player_pattern = pattern['player_pattern']

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
            possible_patterns.append({
                'code_pattern': [
                    code_pattern[0].__name__,
                    code_pattern[1].__name__,
                    code_pattern[2].__name__,
                    code_pattern[3].__name__,
                ],
                'player_pattern': player_pattern,
            })

    return possible_patterns


if __name__ == '__main__':

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
    # [{
    #     code_pattern: [...],   <-- 実行された可能性のあるコードの順番
    #     player_pattern: [...], <-- その場合のプレイヤーの順番
    # }, ...]
    guesses_for_first_game = run(
        hp=drone_after_first_game.hp,
        location=drone_after_first_game.location,
        inventory=drone_after_first_game.inventory,
    )
    for _ in guesses_for_first_game:
        print('1st', _)

    # 2nd game の結果を入力してね。
    drone_after_second_game = Drone(
        hp=-1,
        location=Location.RED,
        inventory=[
            ITEM[Location.RED],
            ITEM[Location.PURPLE],
        ],
    )
    # こちらが 1st game の結果により推測される、player_patterns です。
    guessed_player_patterns = map(lambda x: x['player_pattern'], guesses_for_first_game)
    # こちらが 2nd game で実行されたと考えられるコードの羅列。
    guesses_for_second_game = run(
        hp=drone_after_second_game.hp,
        location=drone_after_second_game.location,
        inventory=drone_after_second_game.inventory,
        player_patterns=guessed_player_patterns,
    )
    for _ in guesses_for_second_game:
        print('2nd', _)
