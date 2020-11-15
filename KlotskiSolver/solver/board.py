import numpy as np
import enum


class BlockType(enum.Enum):
    FourSquare = 1
    TwoHorizontal = 2
    TwoVertical = 3
    Single = 4


class Block:
    def __init__(self, occupying, block_type: BlockType):
        self.occupying = np.array(occupying, dtype=int)  # type:np.ndarray
        self.block_type = block_type  # type: BlockType

    def move_up(self):
        return Block(self.occupying + [0, -1], self.block_type)

    def move_down(self):
        return Block(self.occupying + [0, 1], self.block_type)

    def move_left(self):
        return Block(self.occupying + [-1, 0], self.block_type)

    def move_right(self):
        return Block(self.occupying + [1, 0], self.block_type)

    def clone(self):
        return Block(self.occupying.copy(), self.block_type)

    def __repr__(self):
        return repr(self.occupying)


class Board:
    def __init__(self, blocks, height, width):
        self.height = height
        self.width = width
        self.blocks = blocks
        self.state = np.zeros((width, height), int)
        for block in self.blocks:
            indices = [tuple(coor) for coor in block.occupying]
            self.state[tuple(np.transpose(indices))] = block.block_type.value
        self.state.flags.writeable = False

    @classmethod
    def standard_layout(cls):
        caocao = Block([[1, 0], [2, 0], [1, 1], [2, 1]], BlockType.FourSquare)
        zhangfei = Block([[0, 0], [0, 1]], BlockType.TwoVertical)
        machao = Block([[3, 0], [3, 1]], BlockType.TwoVertical)
        zhaoyun = Block([[0, 2], [0, 3]], BlockType.TwoVertical)
        huangzhong = Block([[3, 2], [3, 3]], BlockType.TwoVertical)
        guanyu = Block([[1, 2], [2, 2]], BlockType.TwoHorizontal)
        zu1 = Block([[0, 4]], BlockType.Single)
        zu2 = Block([[1, 3]], BlockType.Single)
        zu3 = Block([[2, 3]], BlockType.Single)
        zu4 = Block([[3, 4]], BlockType.Single)
        return cls([caocao, zhangfei, machao, zhaoyun, huangzhong, guanyu, zu1, zu2, zu3, zu4], 5, 4)

    def __eq__(self, other):
        return np.array_equal(self.state, other.state)

    def __hash__(self):
        return hash(self.state.tobytes())

    def __repr__(self):
        return str(self.state.transpose())

    def generate_possible_moves(self):
        moves = []

        def can_move(orig_pos, new_pos):
            orig_pos = [tuple(coor) for coor in orig_pos]
            new_pos = [tuple(coor) for coor in new_pos]
            needed = [coor for coor in new_pos if coor not in orig_pos]
            for x, y in needed:
                if x < 0 or x >= self.width:
                    return False
                if y < 0 or y >= self.height:
                    return False
            return np.all(self.state[tuple(np.transpose(needed))] == 0)

        def process_move(orig_block: Block, new_block: Block):
            if can_move(orig_block.occupying, new_block.occupying):
                new_blocks = [new_block if blk == orig_block else blk for blk in self.blocks]
                moves.append(Board(new_blocks, self.height, self.width))

        for block in self.blocks:
            # if move up
            process_move(block, block.move_up())
            # if move down
            process_move(block, block.move_down())
            # if move left
            process_move(block, block.move_left())
            # if move right
            process_move(block, block.move_right())
        return moves
