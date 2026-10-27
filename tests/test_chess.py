import unittest
import Chess

class ChessRulesTests(unittest.TestCase):
    def setUp(self):
        Chess.initBoard()

    def play(self, source, target, turn):
        r1, c1, _, _ = Chess.parseInput(source)
        r2, c2, _, _ = Chess.parseInput(target)
        self.assertTrue(Chess.isValidMove(r1, c1, r2, c2, turn, Chess.board), (source, target))
        position = Chess.copyBoard(Chess.board)
        Chess.makeMove(r1, c1, r2, c2, position)
        self.assertFalse(Chess.isKingInCheck(turn, position))
        Chess.makeMove(r1, c1, r2, c2, Chess.board, update_state=True)

    def test_initial_position_has_twenty_legal_moves(self):
        moves = sum(len(Chess.getValidMoves(r, c, 1, Chess.board)) for r in range(8) for c in range(8) if Chess.board[r][c] > 0)
        self.assertEqual(moves, 20)

    def test_coordinate_parser_requires_the_entire_input_to_match(self):
        self.assertEqual(Chess.parseInput("E2"), (6, 4, None, None))
        self.assertEqual(Chess.parseInput("e2e4"), (6, 4, 4, 4))
        for value in ("e2e4junk", "e9", "i2", "e2-e4", ""):
            self.assertIsNone(Chess.parseInput(value), value)

    def test_pawns_cannot_capture_forward_or_move_sideways(self):
        self.assertFalse(Chess.isValidMove(6, 4, 5, 5, 1, Chess.board))
        self.assertFalse(Chess.isValidMove(6, 4, 6, 5, 1, Chess.board))

    def test_king_cannot_capture_the_opposing_king(self):
        Chess.board = [[0] * 8 for _ in range(8)]
        Chess.board[7][4], Chess.board[0][4] = 6, -6
        self.assertFalse(Chess.isValidMove(7, 4, 0, 4, 1, Chess.board))

    def test_en_passant_is_available_for_one_reply_and_removes_captured_pawn(self):
        self.play("e2", "e4", 1)
        self.play("a7", "a6", -1)
        self.play("e4", "e5", 1)
        self.play("d7", "d5", -1)
        self.assertTrue(Chess.isValidMove(3, 4, 2, 3, 1, Chess.board))
        position = Chess.copyBoard(Chess.board)
        Chess.makeMove(3, 4, 2, 3, position)
        self.assertEqual(position[3][3], 0)
        self.assertEqual(position[2][3], 1)
        Chess.makeMove(3, 4, 2, 3, Chess.board, update_state=True)
        self.assertIsNone(Chess.en_passant_target)

    def test_en_passant_expires_after_one_reply(self):
        self.play("e2", "e4", 1)
        self.play("a7", "a6", -1)
        self.play("e4", "e5", 1)
        self.play("d7", "d5", -1)
        self.play("a2", "a3", 1)
        self.assertIsNone(Chess.en_passant_target)
        self.assertFalse(Chess.isValidMove(3, 4, 2, 3, 1, Chess.board))

    def test_castling_moves_the_rook_and_revokes_both_rights(self):
        for source, target, turn in (("e2","e4",1),("e7","e5",-1),("g1","f3",1),("b8","c6",-1),("f1","c4",1),("g8","f6",-1)):
            self.play(source,target,turn)
        self.assertTrue(Chess.isValidMove(7,4,7,6,1,Chess.board))
        Chess.makeMove(7,4,7,6,Chess.board,update_state=True)
        self.assertEqual(Chess.board[7][5],2)
        self.assertFalse(Chess.castling_rights["K"])
        self.assertFalse(Chess.castling_rights["Q"])

    def test_castling_through_check_is_rejected(self):
        Chess.board = [[0] * 8 for _ in range(8)]
        Chess.board[7][4], Chess.board[7][7] = 6, 2
        Chess.board[0][0], Chess.board[0][4] = -6, -2
        Chess.castling_rights["K"] = True
        self.assertFalse(Chess.isValidMove(7,4,7,6,1,Chess.board))

    def test_en_passant_that_exposes_the_king_to_a_rook_is_illegal(self):
        Chess.board = [[0] * 8 for _ in range(8)]
        Chess.board[3][4], Chess.board[0][0] = 6, -6
        Chess.board[3][5], Chess.board[3][6], Chess.board[3][7] = 1, -1, -2
        Chess.en_passant_target = (2, 6)
        self.assertTrue(Chess.isValidMove(3, 5, 2, 6, 1, Chess.board))
        self.assertNotIn((3,5,2,6), Chess.getValidMoves(3,5,1,Chess.board))

    def test_a_pinned_piece_cannot_leave_its_king_exposed(self):
        Chess.board = [[0] * 8 for _ in range(8)]
        Chess.board[7][4], Chess.board[6][4], Chess.board[0][4], Chess.board[0][0] = 6, 2, -2, -6
        self.assertNotIn((6,4,6,5), Chess.getValidMoves(6,4,1,Chess.board))

    def test_fools_mate_is_checkmate(self):
        for source, target, turn in (("f2", "f3", 1), ("e7", "e5", -1), ("g2", "g4", 1), ("d8", "h4", -1)):
            self.play(source, target, turn)
        self.assertTrue(Chess.isKingInCheck(1, Chess.board))
        self.assertTrue(Chess.isCheckmate(1))

    def test_stalemate_is_detected_without_check(self):
        Chess.board = [[0] * 8 for _ in range(8)]
        Chess.board[0][0], Chess.board[2][2], Chess.board[2][1] = -6, 6, 5
        self.assertFalse(Chess.isKingInCheck(-1, Chess.board))
        self.assertTrue(Chess.isStalemate(-1))

if __name__ == "__main__":
    unittest.main()
