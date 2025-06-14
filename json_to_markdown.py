#!/usr/bin/env python3
import json
import click
from pathlib import Path
from rich import print
from rich.console import Console
from rich.table import Table
from translations import translate, translate_list

console = Console()

class STSRunParser:
    def __init__(self, json_data, lang="en", show_deck_details=False):
        self.data = json_data
        self.lang = lang
        self.show_deck_details = show_deck_details
        self.initial_deck = self._get_initial_deck()
        self.initial_relics = self._get_initial_relics()
        
    def get_floor_data(self, floor):
        floor_index = floor - 1
        prev_floor_index = floor_index - 1 if floor_index > 0 else None
        
        floor_data = {
            "floor": floor,
            "path": self._safe_get_list("path_per_floor", floor_index),
            "gold": self._safe_get_list("gold_per_floor", floor_index),
            "gold_prev": self._safe_get_list("gold_per_floor", prev_floor_index) if prev_floor_index is not None else None,
            "current_hp": self._safe_get_list("current_hp_per_floor", floor_index),
            "current_hp_prev": self._safe_get_list("current_hp_per_floor", prev_floor_index) if prev_floor_index is not None else None,
            "max_hp": self._safe_get_list("max_hp_per_floor", floor_index),
            "max_hp_prev": self._safe_get_list("max_hp_per_floor", prev_floor_index) if prev_floor_index is not None else None,
            "potions_obtained": self._get_potions_for_floor(floor),
            "cards_obtained": self._get_cards_for_floor(floor),
            "relics_obtained": self._get_relics_for_floor(floor),
            "damage_taken": self._get_damage_for_floor(floor),
            "campfire_choices": self._get_campfire_for_floor(floor),
            "shop_contents": self._get_shop_for_floor(floor),
            "shop_purchases": self._get_shop_purchases_for_floor(floor),
            "event_choices": self._get_event_for_floor(floor)
        }
        
        return floor_data
    
    def _safe_get_list(self, key, index):
        lst = self.data.get(key, [])
        if index is not None and index < len(lst):
            return lst[index]
        return None
    
    def _get_potions_for_floor(self, floor):
        potions = []
        for potion in self.data.get("potions_obtained", []):
            if potion.get("floor") == floor:
                potions.append(potion.get("key"))
        return potions
    
    def _get_cards_for_floor(self, floor):
        for choice in self.data.get("card_choices", []):
            if choice.get("floor") == floor:
                return choice
        return None
    
    def _get_relics_for_floor(self, floor):
        relics = []
        for relic in self.data.get("relics_obtained", []):
            if relic.get("floor") == floor:
                relics.append(relic.get("key"))
        return relics
    
    def _get_damage_for_floor(self, floor):
        for damage in self.data.get("damage_taken", []):
            if damage.get("floor") == floor:
                return {
                    "enemies": damage.get("enemies"),
                    "damage": damage.get("damage"),
                    "turns": damage.get("turns")
                }
        return None
    
    def _get_campfire_for_floor(self, floor):
        for choice in self.data.get("campfire_choices", []):
            if choice.get("floor") == floor:
                return {
                    "action": choice.get("key"),
                    "data": choice.get("data")
                }
        return None
    
    def _get_shop_for_floor(self, floor):
        for shop in self.data.get("shop_contents", []):
            if shop.get("floor") == floor:
                return shop
        return None
    
    def _get_shop_purchases_for_floor(self, floor):
        """ショップでの購入・パージ行動を取得"""
        purchases = []
        
        # アイテム購入
        items_purchased = self.data.get("items_purchased", [])
        item_purchase_floors = self.data.get("item_purchase_floors", [])
        
        for i, purchase_floor in enumerate(item_purchase_floors):
            if purchase_floor == floor and i < len(items_purchased):
                purchases.append({
                    "type": "purchase",
                    "item": items_purchased[i]
                })
        
        # カードパージ
        purchased_purges = self.data.get("purchased_purges", 0)
        items_purged_floors = self.data.get("items_purged_floors", [])
        items_purged = self.data.get("items_purged", [])
        
        purge_count = 0
        for purge_floor in items_purged_floors:
            if purge_floor == floor:
                if purge_count < len(items_purged):
                    purchases.append({
                        "type": "purge",
                        "item": items_purged[purge_count]
                    })
                else:
                    purchases.append({
                        "type": "purge",
                        "item": "Unknown Card"
                    })
                purge_count += 1
        
        return purchases
    
    def _get_initial_deck(self):
        """初期デッキを取得"""
        character = self.data.get('character_chosen', 'IRONCLAD')
        
        # 基本的な初期デッキ
        if character == 'IRONCLAD':
            return ["Strike_R"] * 5 + ["Defend_R"] * 4 + ["Bash"] + ["AscendersBane"]
        elif character == 'THE_SILENT':
            return ["Strike_G"] * 5 + ["Defend_G"] * 5 + ["Neutralize"] + ["Survivor"] + ["AscendersBane"]
        elif character == 'DEFECT':
            return ["Strike_B"] * 4 + ["Defend_B"] * 4 + ["Zap"] + ["Dualcast"] + ["AscendersBane"]
        elif character == 'WATCHER':
            return ["Strike_P"] * 4 + ["Defend_P"] * 4 + ["Eruption"] + ["Vigilance"] + ["AscendersBane"]
        else:
            return ["AscendersBane"]
    
    def _get_initial_relics(self):
        """初期レリックを取得"""
        character = self.data.get('character_chosen', 'IRONCLAD')
        
        if character == 'IRONCLAD':
            return ["Burning Blood"]
        elif character == 'THE_SILENT':
            return ["Ring of the Snake"]
        elif character == 'DEFECT':
            return ["Cracked Core"]
        elif character == 'WATCHER':
            return ["Pure Water"]
        else:
            return []
    
    def _get_deck_at_floor(self, floor):
        """指定階層でのデッキを取得"""
        deck = self.initial_deck.copy()
        
        # Neowボーナスでのカード取得
        neow_bonus = self.data.get('neow_bonus', '')
        if 'RANDOM_COLORLESS' in neow_bonus or 'THREE_RARE_CARDS' in neow_bonus:
            # 階層0のカード選択を確認
            for choice in self.data.get("card_choices", []):
                if choice.get("floor") == 0:
                    picked = choice.get("picked")
                    if picked and picked != "SKIP":
                        deck.append(picked)
                    break
        
        # 各階層で取得したカードを追加
        for choice in self.data.get("card_choices", []):
            if 0 < choice.get("floor", 999) <= floor:
                picked = choice.get("picked")
                if picked and picked != "SKIP":
                    deck.append(picked)
        
        # ショップで購入したカードを追加
        items_purchased = self.data.get("items_purchased", [])
        item_purchase_floors = self.data.get("item_purchase_floors", [])
        for i, purchase_floor in enumerate(item_purchase_floors):
            if purchase_floor <= floor and i < len(items_purchased):
                item = items_purchased[i]
                # カードかどうかをチェック（レリックでない場合）
                if item not in self._get_all_relics_up_to_floor(floor):
                    deck.append(item)
        
        # イベントでのカード変換・取得を考慮
        for event in self.data.get("event_choices", []):
            if event.get("floor", 999) <= floor:
                # カード削除
                cards_removed = event.get("cards_removed", [])
                for card in cards_removed:
                    if card in deck:
                        deck.remove(card)
                
                # カード変換・取得（必要に応じて拡張）
        
        # パージしたカードを削除
        items_purged = self.data.get("items_purged", [])
        items_purged_floors = self.data.get("items_purged_floors", [])
        for i, purge_floor in enumerate(items_purged_floors):
            if purge_floor <= floor and i < len(items_purged):
                card = items_purged[i]
                if card in deck:
                    deck.remove(card)
        
        # アップグレードの処理
        for campfire in self.data.get("campfire_choices", []):
            if campfire.get("floor", 999) <= floor and campfire.get("key") == "SMITH":
                card_to_upgrade = campfire.get("data")
                if card_to_upgrade and card_to_upgrade in deck:
                    deck[deck.index(card_to_upgrade)] = card_to_upgrade + "+1"
        
        # イベントでのアップグレード
        for event in self.data.get("event_choices", []):
            if event.get("floor", 999) <= floor:
                cards_upgraded = event.get("cards_upgraded", [])
                for card in cards_upgraded:
                    if card in deck:
                        deck[deck.index(card)] = card + "+1"
        
        return sorted(deck)
    
    def _get_all_relics_up_to_floor(self, floor):
        """指定階層までに取得した全レリックのリスト"""
        relics = self.initial_relics.copy()
        
        # Neowボーナスでのレリック取得
        neow_bonus = self.data.get('neow_bonus', '')
        if 'BOSS_RELIC' in neow_bonus:
            # Neowボーナスログからレリックを確認
            neow_log = self.data.get('neow_bonus_log', {})
            relics_obtained = neow_log.get('relicsObtained', [])
            relics.extend(relics_obtained)
        
        # 各階層で取得したレリック
        for relic in self.data.get("relics_obtained", []):
            if relic.get("floor", 999) <= floor:
                relics.append(relic.get("key"))
        
        # ショップで購入したレリック
        items_purchased = self.data.get("items_purchased", [])
        item_purchase_floors = self.data.get("item_purchase_floors", [])
        shop_relics = []
        for shop in self.data.get("shop_contents", []):
            if shop.get("floor", 999) <= floor:
                shop_relics.extend(shop.get("relics", []))
        
        for i, purchase_floor in enumerate(item_purchase_floors):
            if purchase_floor <= floor and i < len(items_purchased):
                item = items_purchased[i]
                if item in shop_relics:
                    relics.append(item)
        
        return relics
    
    def _get_relics_at_floor(self, floor):
        """指定階層でのレリックを取得"""
        return self._get_all_relics_up_to_floor(floor)
    
    def _get_potions_at_floor(self, floor):
        """指定階層でのポーションを取得（スロット管理）"""
        potion_slots = 2  # 基本スロット数
        potions = []
        
        # ポーションベルトチェック
        if "Potion Belt" in self._get_relics_at_floor(floor):
            potion_slots = 4
        
        # 各階層でのポーション取得・使用・破棄を追跡
        for f in range(1, floor + 1):
            # 取得
            for potion in self.data.get("potions_obtained", []):
                if potion.get("floor") == f:
                    if len(potions) < potion_slots:
                        potions.append(potion.get("key"))
            
            # 使用
            potion_use = self.data.get("potion_use_per_floor", [])
            if f - 1 < len(potion_use):
                used_potions = potion_use[f - 1]
                for used in used_potions:
                    if used in potions:
                        potions.remove(used)
            
            # 破棄
            potion_discard = self.data.get("potion_discard_per_floor", [])
            if f - 1 < len(potion_discard):
                discarded_potions = potion_discard[f - 1]
                for discarded in discarded_potions:
                    if discarded in potions:
                        potions.remove(discarded)
        
        return potions
    
    def _get_event_for_floor(self, floor):
        for event in self.data.get("event_choices", []):
            if event.get("floor") == floor:
                return event
        return None
    
    def to_markdown(self):
        lines = []
        
        # ヘッダー情報
        character = translate(self.data.get('character_chosen', 'Unknown'), self.lang)
        lines.append(f"# Slay the Spire Run - {character}")
        lines.append("")
        lines.append(f"**{translate('seed', self.lang)}**: {self.data.get('seed_played', 'Unknown')}")
        lines.append(f"**{translate('ascension_level', self.lang)}**: {self.data.get('ascension_level', 0)}")
        lines.append(f"**{translate('floor_reached', self.lang)}**: {self.data.get('floor_reached', 0)}")
        victory_text = translate('yes' if self.data.get('victory', False) else 'no', self.lang)
        lines.append(f"**{translate('victory', self.lang)}**: {victory_text}")
        if not self.data.get('victory', False):
            killed_by = translate(self.data.get('killed_by', 'Unknown'), self.lang)
            lines.append(f"**{translate('killed_by', self.lang)}**: {killed_by}")
        lines.append(f"**{translate('score', self.lang)}**: {self.data.get('score', 0)}")
        lines.append(f"**{translate('playtime', self.lang)}**: {self.data.get('playtime', 0)} {translate('seconds', self.lang)}")
        lines.append("")
        
        
        # 最終デッキ
        lines.append(f"## {translate('final_deck', self.lang)}")
        master_deck = self.data.get('master_deck', [])
        for card in master_deck:
            lines.append(f"- {translate(card, self.lang)}")
        lines.append("")
        
        # 最終レリック
        lines.append(f"## {translate('final_relics', self.lang)}")
        relics = self.data.get('relics', [])
        for relic in relics:
            lines.append(f"- {translate(relic, self.lang)}")
        lines.append("")
        
        # 階層ごとの詳細
        lines.append(f"## {translate('floor_details', self.lang)}")
        lines.append("")
        
        # Neowボーナス選択（階層0として表示）
        lines.append(f"### {translate('neow_bonus', self.lang)}")
        bonus = translate(self.data.get('neow_bonus', 'Unknown'), self.lang)
        lines.append(f"- **{translate('bonus', self.lang)}**: {bonus}")
        cost = translate(self.data.get('neow_cost', 'Unknown'), self.lang)
        lines.append(f"- **{translate('cost', self.lang)}**: {cost}")
        
        # カード選択（階層0のカード選択があれば表示）
        neow_card_choice = None
        for choice in self.data.get("card_choices", []):
            if choice.get("floor") == 0:
                neow_card_choice = choice
                break
        
        if neow_card_choice:
            picked = neow_card_choice.get('picked', '')
            not_picked = neow_card_choice.get('not_picked', []) or []
            
            translated_cards = []
            if not_picked:
                for card in not_picked:
                    translated_cards.append(translate(card, self.lang))
            if picked:
                translated_cards.append(f"({translate(picked, self.lang)})")
            
            if translated_cards:
                lines.append(f"- **{translate('card_choice', self.lang)}**: {', '.join(translated_cards)}")
        
        lines.append("")
        
        floor_reached = self.data.get('floor_reached', 0)
        for floor in range(1, floor_reached + 1):
            floor_data = self.get_floor_data(floor)
            
            path = translate(floor_data['path'] or '?', self.lang)
            lines.append(f"### {translate('floor', self.lang)} {floor} - {path}")
            
            # 現在の所有物（折りたたみ可能）
            current_deck = self._get_deck_at_floor(floor - 1)  # 階層開始時点なので-1
            current_relics = self._get_relics_at_floor(floor - 1)
            current_potions = self._get_potions_at_floor(floor - 1)
            
            # デッキ（枚数のみ表示、詳細はオプション）
            deck_count = len(current_deck)
            if self.show_deck_details:
                translated_deck = translate_list(current_deck, self.lang)
                # カードごとの出現回数をカウント
                from collections import Counter
                card_counts = Counter(translated_deck)
                deck_display = []
                for card, count in sorted(card_counts.items()):
                    if count > 1:
                        deck_display.append(f"{card} x{count}")
                    else:
                        deck_display.append(card)
                lines.append(f"- **{translate('current_deck', self.lang)}** ({deck_count} {translate('card_count', self.lang)}): {', '.join(deck_display)}")
            else:
                lines.append(f"- **{translate('current_deck', self.lang)}**: {deck_count} {translate('card_count', self.lang)}")
            
            # レリック
            if current_relics:
                translated_relics = translate_list(current_relics, self.lang)
                lines.append(f"- **{translate('current_relics', self.lang)}**: {', '.join(translated_relics)}")
            
            # ポーション
            if current_potions:
                translated_potions = translate_list(current_potions, self.lang)
                lines.append(f"- **{translate('current_potions', self.lang)}**: {', '.join(translated_potions)}")
            
            # HP とゴールド
            if floor_data['current_hp'] is not None:
                hp_diff = ""
                if floor_data['current_hp_prev'] is not None:
                    diff = floor_data['current_hp'] - floor_data['current_hp_prev']
                    if diff != 0:
                        hp_diff = f" ({diff:+d})"
                
                max_hp_diff = ""
                if floor_data['max_hp_prev'] is not None and floor_data['max_hp'] != floor_data['max_hp_prev']:
                    max_diff = floor_data['max_hp'] - floor_data['max_hp_prev']
                    max_hp_diff = f" ({max_diff:+d})"
                
                lines.append(f"- **{translate('hp', self.lang)}**: {floor_data['current_hp']}{hp_diff}/{floor_data['max_hp']}{max_hp_diff}")
            
            if floor_data['gold'] is not None:
                gold_diff = ""
                if floor_data['gold_prev'] is not None:
                    diff = floor_data['gold'] - floor_data['gold_prev']
                    if diff != 0:
                        gold_diff = f" ({diff:+d})"
                lines.append(f"- **{translate('gold', self.lang)}**: {floor_data['gold']}{gold_diff}")
            
            # 戦闘情報
            if floor_data['damage_taken']:
                damage = floor_data['damage_taken']
                enemies = translate(damage['enemies'], self.lang)
                lines.append(f"- **{translate('combat', self.lang)}**: {enemies} ({translate('damage', self.lang)}: {damage['damage']}, {translate('turns', self.lang)}: {damage['turns']})")
            
            # 取得アイテム
            if floor_data['cards_obtained']:
                card_choice = floor_data['cards_obtained']
                if card_choice:
                    picked = card_choice.get('picked', '')
                    not_picked = card_choice.get('not_picked', []) or []
                    
                    translated_cards = []
                    for card in not_picked:
                        translated_cards.append(translate(card, self.lang))
                    if picked:
                        translated_cards.append(f"({translate(picked, self.lang)})")
                    
                    if translated_cards:
                        lines.append(f"- **{translate('card_choice', self.lang)}**: {', '.join(translated_cards)}")
            
            if floor_data['relics_obtained']:
                translated_relics = translate_list(floor_data['relics_obtained'], self.lang)
                lines.append(f"- **{translate('relic_obtained', self.lang)}**: {', '.join(translated_relics)}")
            
            if floor_data['potions_obtained']:
                translated_potions = translate_list(floor_data['potions_obtained'], self.lang)
                lines.append(f"- **{translate('potion_obtained', self.lang)}**: {', '.join(translated_potions)}")
            
            # 休憩所
            if floor_data['campfire_choices']:
                campfire = floor_data['campfire_choices']
                if campfire:
                    action = translate(campfire.get('action', ''), self.lang)
                    data = campfire.get('data')
                    if data:
                        data_translated = translate(data, self.lang)
                        lines.append(f"- **{translate('campfire', self.lang)}**: {action} ({data_translated})")
                    else:
                        lines.append(f"- **{translate('campfire', self.lang)}**: {action}")
            
            # ショップ
            if floor_data['shop_contents']:
                shop = floor_data['shop_contents']
                if shop:
                    lines.append(f"- **{translate('shop', self.lang)}**:")
                    if shop.get('cards'):
                        translated_cards = translate_list(shop['cards'], self.lang)
                        lines.append(f"  - {translate('cards', self.lang)}: {', '.join(translated_cards)}")
                    if shop.get('relics'):
                        translated_relics = translate_list(shop['relics'], self.lang)
                        lines.append(f"  - {translate('relics', self.lang)}: {', '.join(translated_relics)}")
                    if shop.get('potions'):
                        translated_potions = translate_list(shop['potions'], self.lang)
                        lines.append(f"  - {translate('potions', self.lang)}: {', '.join(translated_potions)}")
                    
                    # ショップでの購入行動
                    if floor_data['shop_purchases']:
                        purchases = floor_data['shop_purchases']
                        purchase_actions = []
                        for purchase in purchases:
                            if purchase['type'] == 'purchase':
                                translated_item = translate(purchase['item'], self.lang)
                                purchase_actions.append(f"{translate('purchased', self.lang)}: {translated_item}")
                            elif purchase['type'] == 'purge':
                                translated_item = translate(purchase['item'], self.lang)
                                purchase_actions.append(f"{translate('purged', self.lang)}: {translated_item}")
                        
                        if purchase_actions:
                            lines.append(f"  - {translate('shop_purchases', self.lang)}: {', '.join(purchase_actions)}")
            
            # イベント
            if floor_data['event_choices']:
                event = floor_data['event_choices']
                if event:
                    event_name = translate(event.get('event_name', 'Unknown'), self.lang)
                    player_choice = translate(event.get('player_choice', ''), self.lang)
                    lines.append(f"- **{translate('event', self.lang)}**: {event_name} - {player_choice}")
            
            lines.append("")
        
        return "\n".join(lines)

def parse_run_file(file_path, lang="en", show_deck_details=False):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    parser = STSRunParser(data, lang, show_deck_details)
    return parser.to_markdown()

@click.command()
@click.argument('input_dirs', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--output-dir', '-o', default='output', help='Output directory')
@click.option('--lang', '-l', default='en', type=click.Choice(['en', 'ja']), help='Language for output (en/ja)')
@click.option('--show-deck-details', '-d', is_flag=True, help='Show detailed deck contents at each floor')
def main(input_dirs, output_dir, lang, show_deck_details):
    """Convert JSON files in the input directories to Markdown format."""
    output_path = Path(output_dir)
    
    # 出力ディレクトリの作成
    output_path.mkdir(exist_ok=True)
    
    all_run_files = []
    
    # 各入力ディレクトリから.runファイルを収集
    for input_dir in input_dirs:
        input_path = Path(input_dir)
        
        # runsディレクトリの場合は再帰的に探索
        if input_path.name.lower() == 'runs':
            # 再帰的に.runファイルを探す
            run_files = list(input_path.rglob("*.run"))
            
            if run_files:
                console.print(f"[cyan]{input_path.name}[/cyan] ディレクトリから {len(run_files)} 個のファイルを見つけました（再帰的検索）")
                
                # ファイルごとにキャラクターを判定
                for run_file in run_files:
                    # ファイル内容からキャラクターを判定
                    try:
                        with open(run_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            character = data.get('character_chosen', 'UNKNOWN')
                            
                        # キャラクター別サブディレクトリを作成
                        char_output_path = output_path / character
                        char_output_path.mkdir(exist_ok=True)
                        
                        all_run_files.append((run_file, char_output_path))
                    except Exception as e:
                        console.print(f"[yellow]警告[/yellow]: {run_file.name} の読み込みに失敗しました: {e}")
            else:
                console.print(f"[yellow]警告[/yellow]: {input_path.name} に .runファイルが見つかりません")
        else:
            # 通常のディレクトリは今まで通りの処理
            run_files = list(input_path.glob("*.run"))
            
            if run_files:
                console.print(f"[cyan]{input_path.name}[/cyan] ディレクトリから {len(run_files)} 個のファイルを見つけました")
                
                # キャラクター別サブディレクトリを作成
                char_output_path = output_path / input_path.name
                char_output_path.mkdir(exist_ok=True)
                
                for run_file in run_files:
                    all_run_files.append((run_file, char_output_path))
            else:
                console.print(f"[yellow]警告[/yellow]: {input_path.name} に .runファイルが見つかりません")
    
    if not all_run_files:
        console.print("[red]エラー: .runファイルが見つかりません。[/red]")
        return
    
    console.print(f"[green]合計 {len(all_run_files)} 個のファイルを処理します...[/green]")
    
    for run_file, char_output_path in all_run_files:
        try:
            console.print(f"Processing: {run_file.parent.name}/{run_file.name}")
            
            # Markdownの生成
            markdown_content = parse_run_file(run_file, lang, show_deck_details)
            
            # 出力ファイル名の生成
            output_file = char_output_path / f"{run_file.stem}.md"
            
            # ファイルの書き込み
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            console.print(f"[green]✓[/green] {char_output_path.name}/{output_file.name} を生成しました")
            
        except Exception as e:
            import traceback
            console.print(f"[red]エラー[/red]: {run_file.name} の処理中にエラーが発生しました: {e}")
            console.print(f"[red]詳細[/red]: {traceback.format_exc()}")
    
    console.print(f"\n[green]完了![/green] Markdownファイルは {output_path} に保存されました。")

if __name__ == "__main__":
    main()