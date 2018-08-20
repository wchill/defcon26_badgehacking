# this is so untested it's not even funny

.data

.text

main:
	addiu $sp, -1536
	sw $ra, -4($sp)
	sw $fp, -8($sp)
	sw $s0, -12($sp)
	sw $s1, -16($sp)
	sw $s2, -20($sp)
	move $fp, $sp

	# calculate address to output buffer - we need 1280 bytes of ram for this
	# we will have 256 bytes of scratch space afterwards, minus some space for registers

	# initialize state
	# s0 will hold the output buffer address
	# s1 will hold the current address
	addiu $s0, $fp, -1536
	move $s1, $zero

	# zero out the string
	sw $s1, 0($s0)

main_loop:
	addi $t0, $fp, -128
	li $t1, 0x58343025
	sw $t1, 0($t0)
	sw $zero, 4($t0)

	addi $a0, $fp, -256
	addi $a1, $fp, -128
	move $a2, $s1
	li $t0, 0x9D022D7C		# maybe_sprintf
	jalr $t0
	nop

	addiu $a0, $fp, -1536
	addiu $a1, $fp, -256
	li $t0, 0x9D00018C		# maybe_strcat
	jalr $t0
	nop

	addiu $a0, $fp, -1536
	li $t0, 0x9D0220F4		# maybe_strlen
	jalr $t0
	nop

	# this gets the address of the end of the concatenated string
	addiu $t0, $fp, -1536
	add $t0, $t0, $v0

	li $t1, 58	# colon
	sb $t1, 0($t0)
	li $t1, 20  # space
	sb $t1, 1($t0)
	sb $zero, 2($t0)

	move $s2, $zero

format_word:
	addi $t0, $fp, -128
	li $t1, 0x58343025
	sw $t1, 0($t0)
	sw $zero, 4($t0)

	addi $a0, $fp, -256
	addi $a1, $fp, -128
	lw $a2, 0($s1)
	li $t0, 0x9D022D7C		# maybe_sprintf
	jalr $t0
	nop

	addiu $a0, $fp, -1536
	addiu $a1, $fp, -256
	li $t0, 0x9D00018C		# maybe_strcat
	jalr $t0
	nop

	addiu $a0, $fp, -1536
	li $t0, 0x9D0220F4		# maybe_strlen
	jalr $t0
	nop

	addiu $t0, $fp, -1536
	add $t0, $t0, $v0

	li $t1, 20  # space
	sb $t1, 0($t0)
	sb $zero, 1($t0)

	# increment the read address
	addiu $s1, 4

	# loop check
	addiu $s2, 1
	li $t1, 8
	bne $s2, $t1, format_word
	nop

	li $t1, 13 	# \r
	sb $t1, 0($t0)
	li $t1, 10	# \n
	sb $t1, 1($t0)
	sb $zero, 2($t0)

finish:
	# check to see if we finished reading RAM
	li $t1, 0x200
	bne $s1, $t1, main_loop
	nop

	move $a0, $s0
	li $t0, 0x9D0220F4		# maybe_strlen
	jalr $t0
	nop

	# print
	li $a0, 0x80000364		# word_80000364
	move $a1, $s0
	move $a2, $v0
	li $t0, 0x9D09518		# maybe_print_to_console
	jalr $t0
	nop

	move $sp, $fp
	lw $s2, -20($sp)
	lw $s1, -16($sp)
	lw $s0, -12($sp)
	lw $fp, -8($sp)
	lw $ra, -4($sp)
	addiu $sp, 1536
	jr $ra
	nop