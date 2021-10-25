import java.awt.Cursor;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.Dimension;
import java.awt.Font;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JLabel;
import javax.swing.BoxLayout;
import javax.swing.JOptionPane;

import java.util.ArrayList;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;

@SuppressWarnings("serial")
public final class Buttons extends JFrame implements ActionListener {
    private static final int grid[][] = {{1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1}, {1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1}, {1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1}, {1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1}, {1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1}, {1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1}, {1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1}, {1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1}, {1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1}, {1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1}, {1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1}, {1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1}, {1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1}, {1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1}, {1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1}, {1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1}, {1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1}, {1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1}, {1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1}, {1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1}, {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1}};

    private final int rows;
    private final int cols;
    private final JLabel movesLabel;
    private final JButton resetButton;
    private final JButton[][] buttons;

    // Current position in maze
    private int posRow;
    private int posCol;

    private final int endRow;
    private final int endCol;

    private static final int MAX_MOVES = 139;
    private ArrayList<Integer> moveHistory;

    public static void main(String[] args) throws Exception
    {
        new Buttons();
    }

    public Buttons() {
        super("Buttons!");

        this.resetValues();

        this.rows = grid.length;
        this.cols = grid[0].length;

        this.endRow = rows - 1;
        this.endCol = cols - 2;

        JPanel containerPanel = new JPanel();
        containerPanel.setLayout(new BoxLayout(containerPanel, BoxLayout.PAGE_AXIS));
        JPanel buttonPanel = new JPanel(new GridLayout(rows, cols));
        JPanel controlPanel = new JPanel();

        this.buttons = new JButton[rows][cols];

        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                this.buttons[row][col] = new JButton("?");
                this.buttons[row][col].addActionListener(this);
                this.buttons[row][col].setActionCommand(
                    Integer.toString(col + row * cols)
                );
                buttonPanel.add(this.buttons[row][col]);
            }
        }

        this.buttons[endRow][endCol].setText("⚑");
        buttonPanel.setPreferredSize(new Dimension(45 * rows, 45 * cols));

        this.movesLabel = new JLabel("Moves left: 20");
        controlPanel.add(this.movesLabel);

        this.resetButton = new JButton("Reset");
        this.resetButton.addActionListener(this);
        this.resetButton.setActionCommand("reset");
        controlPanel.add(this.resetButton);

        containerPanel.add(buttonPanel);
        containerPanel.add(controlPanel);

        this.resetGUI();

        this.getContentPane().add(containerPanel);
        this.pack();
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        this.setVisible(true);
    }

    private void resetValues()
    {
        this.posRow = 0;
        this.posCol = 1;
        this.moveHistory = new ArrayList<>();
        this.moveHistory.add(posCol + posRow * cols);
    }

    private void updateMovesLeft()
    {
        this.movesLabel.setText(
            "Moves left: " + Integer.toString(MAX_MOVES - this.moveHistory.size())
        );
    }

    private void resetGUI()
    {
        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                // this.buttons[row][col].setEnabled(grid[row][col] != 1);
                this.buttons[row][col].setEnabled(true);
            }
        }

        for (int move : moveHistory) {
            int row = move / cols;
            int col = move % cols;
            this.buttons[row][col].setEnabled(false);
        }

        this.updateMovesLeft();
    }

    private void reset()
    {
        this.resetValues();
        this.resetGUI();
    }

    private boolean isLegalMove(int row, int col)
    {
        if (MAX_MOVES - this.moveHistory.size() <= 0) return false;
        return
            grid[row][col] == 0 &&
            (Math.abs(row - posRow) + Math.abs(col - posCol) == 1);
    }

    private void printFlag()
    {
        BigInteger primes[] = new BigInteger[moveHistory.size()];
        primes[0] = BigInteger.valueOf(2);
        for (int i = 1; i < primes.length; i++) {
            primes[i] = primes[i - 1].nextProbablePrime();
        }

        BigInteger key = BigInteger.valueOf(1);
        BigInteger modulus = new BigInteger("1430313837704837266267655033918654049072573502772041995300810633148485540425442305963378206448908414865491202671058946396326575688430628383447817933039379");

        for (int i = 0; i < this.moveHistory.size(); i++) {
            var move = BigInteger.valueOf(this.moveHistory.get(i));
            key = key.multiply(primes[i].modPow(move, modulus)).mod(modulus);
        }

        BigInteger ciphertext = new BigInteger("1181624346478884506978387685027501257422054115549381320819711748725513305918055802813085700551988448885328987653245675378090761255233757606571908411691314");

        BigInteger plaintext = ciphertext.multiply(key).mod(modulus);
        byte[] plaintextBytes = plaintext.toByteArray();
        String flag = new String(plaintextBytes, StandardCharsets.UTF_8);

        JOptionPane.showMessageDialog(
            this,
            "Congrats! The flag is: " + flag,
            "Flag",
            JOptionPane.INFORMATION_MESSAGE
        );

        System.out.println(flag);
    }

    @Override
    public void actionPerformed(ActionEvent event) {
        String command = event.getActionCommand();
        if (command.equals("reset")) {
            this.reset();
        } else {
            int move = Integer.parseInt(command);
            int row = move / cols;
            int col = move % cols;
            if (this.isLegalMove(row, col)) {
                this.buttons[row][col].setEnabled(false);
                this.posRow = row;
                this.posCol = col;

                this.moveHistory.add(move);
                System.out.println(this.moveHistory);

                this.updateMovesLeft();
                if (this.posRow == this.endRow && this.posCol == this.endCol) {
                    this.printFlag();
                }
            } else {
                JOptionPane.showMessageDialog(
                    this,
                    "Illegal move, you lose ☹",
                    "Illegal move",
                    JOptionPane.ERROR_MESSAGE
                );
                this.reset();
            }
        }
    }
}
