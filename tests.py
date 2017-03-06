import json
import unittest
from datetime import datetime

from blockchain import Block, Blockchain


class TestBlock(unittest.TestCase):
    def test_new_block(self):
        block = Block(1, '12', 1465154705, 'test-block', '12345')

        self.assertEqual(block.index, 1)
        self.assertEqual(block.previous_hash, '12')
        self.assertEqual(block.timestamp, 1465154705)
        self.assertEqual(block.data, 'test-block')
        self.assertEqual(block.hash, '12345')

    def test_block_eq(self):
        block = Block(1, '12', 1465154705, 'test-block', '12345')
        other_block = Block(1, '12', 1465154705, 'test-block', '12345')
        another_block = Block(2, '12', 1465154705, 'test-block', '12345')

        self.assertEqual(block, other_block)
        self.assertNotEqual(block, another_block)

    def test_dict(self):
        block = Block(1, '12', 1465154705, 'test-block', '12345')
        self.assertEqual({'index': 1, 'previous_hash': '12', 'timestamp': 1465154705,
                          'data': 'test-block', 'hash': '12345'}, block.dict())


class TestBlockchain(unittest.TestCase):
    def setUp(self):
        self.blockchain = Blockchain()

    def test_get_genesis_block(self):
        self.assertEqual(Block(0, '0', 1465154705, 'my genesis block!!',
                               '816534932c2b7154836da6afc367695e6337db8a921823784c14378abed4f7d7'),
                         Blockchain.generate_genesis_block())

    def test_calculate_hash(self):
        block = Block(0, '0', 1465154705, 'my genesis block!!',
                      '816534932c2b7154836da6afc367695e6337db8a921823784c14378abed4f7d7')
        self.assertEqual('816534932c2b7154836da6afc367695e6337db8a921823784c14378abed4f7d7',
                         Blockchain.calculate_hash_for_block(block))

    def test_is_valid_new_block(self):
        block = Blockchain.generate_genesis_block()
        block.index = 1
        block.previous_hash = self.blockchain.latest_block.hash
        block.hash = Blockchain.calculate_hash_for_block(block)

        self.assertTrue(self.blockchain.is_valid_new_block(block))

        block.hash = 'a'
        self.assertFalse(self.blockchain.is_valid_new_block(block))

    def test_add_block(self):
        block = Block(self.blockchain.latest_block.index + 1, self.blockchain.latest_block.hash,
                      datetime.utcnow().timestamp(), 'new-block', None)
        block.hash = Blockchain.calculate_hash_for_block(block)

        self.blockchain.add_block(block)

        self.assertEqual(block, self.blockchain.latest_block)

    def test_add_block_invalid(self):
        block = Block(self.blockchain.latest_block.index, self.blockchain.latest_block.hash,
                      datetime.utcnow().timestamp(), 'new-block', None)
        block.hash = Blockchain.calculate_hash_for_block(block)

        self.blockchain.add_block(block)

        self.assertNotEqual(block, self.blockchain.latest_block)

    def test_generate_new_block(self):
        new_block = self.blockchain.generate_new_block('new-block')

        self.assertEqual(1, new_block.index)
        self.assertEqual(Blockchain.generate_genesis_block().hash, new_block.previous_hash)
        self.assertEqual('new-block', new_block.data)
        self.assertEqual(Blockchain.calculate_hash_for_block(new_block), new_block.hash)

    def test_is_valid_chain__wrong_genesis_block(self):
        other_chain = Blockchain()
        other_chain._blockchain[0] = Block(0, '0', 1465154705, 'my genesis block!!', 'aaa')

        self.assertFalse(self.blockchain.is_valid_chain(other_chain.blocks))

    def test_is_valid_chain__wrong_chain(self):
        other_chain = Blockchain()
        new_block = other_chain.generate_new_block('new-block')
        new_block.hash = 'aaa'
        other_chain._blockchain.append(new_block)

        self.assertFalse(self.blockchain.is_valid_chain(other_chain.blocks))

    def test_is_valid_chain__valid_chain(self):
        other_chain = Blockchain()
        other_chain.add_block(other_chain.generate_new_block('new-block'))
        other_chain.add_block(other_chain.generate_new_block('other-new-block'))

        self.assertTrue(self.blockchain.is_valid_chain(other_chain.blocks))

    def replace_chain(self):
        other_chain = Blockchain()
        other_chain.add_block(other_chain.generate_new_block('new-block'))
        new_latest_block = other_chain.add_block(other_chain.generate_new_block('other-new-block'))

        self.blockchain.replace_chain(other_chain.blocks)

        self.assertEqual(new_latest_block, self.blockchain.latest_block)
        self.assertEqual(3, self.blockchain.length)

    def test_json(self):
        self.blockchain.add_block(self.blockchain.generate_new_block('new-block'))
        self.assertEqual(json.dumps([b.dict() for b in self.blockchain.blocks]), self.blockchain.json())
