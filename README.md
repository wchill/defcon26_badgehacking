# defcon26_badgehacking
Notes and things regarding hacking DEFCON 26's badge

## Just want to turn all the letters on your human badge green with the least effort possible and no hardware mods?

1. Use the patcher tool (see its README) on the v2 firmware in the `firmware` folder with the `--solve_p1`, `--pairing_byte 0`, and `--karma_byte 0` patches. (`python patcher.py --solve_p1 --pairing_byte 0 --karma_byte 0 v2_firmware.hex patched_v2_firmware.hex`)

2. Flash patched firmware to badge using a PIC programmer - [see Tymkrs' instructions here](https://github.com/Professor-plum/DefCon26_Badge_Solution/blob/master/resources/Reflashing_The_Badge.docx?raw=True). If you use a PICKit3 and don't solder headers, be warned that you'll have to keep good contact with the pads using your fingers for up to a minute.

3. Reset the badge so that you are in the starting room with no actions taken (just pull the power).

4. Connect to the badge via USB and a terminal emulator.

5. Paste the following string into the terminal (or enter the keys by hand): `>+<v>-<+v--++++-+++-+++++-++-++-+-+-++++-++----++-+----++-++-++-+++-+++++++>v+`

6. Congratulations, you now have a fully green badge!

### Want to do it legitimately on your human badge?

1. Advance all 8 badge types to the point where they have green N, then pair.

2. Short C11 or 2 lower left pins of U5.

3. Flash v2 firmware to badge.

4. Proceed from step 3 above.

## Writeup

(This is going to be a very bad brain dump written at 3 in the morning about 5 weeks after the fact, please forgive any mistakes/inconsistencies)

DEFCON 26 was my first DEFCON - going in, I had no idea what to expect. I had some hobbyist background in all things low level and security related, but I'd say nothing spectacular, just something to dabble with on the weekends. All in all, it was shaping up to be a weekend where I'd kick back, learn something new, go to a few parties and overall just have a chill time with friends.

When we got our attendee packets Thursday morning, I powered up my badge and read the booklet. It looked like a pretty interesting puzzle, but I had no idea just how deep the puzzle went. Overall, Thursday was pretty uneventful - I didn't have a micro USB cable on me at the time to try anything, and I was mostly preoccupied with figuring out where the hell I was supposed to go to get to the various events and what not. I kept an eye on reddit to see what people had figured out with the badges. Someone had dumped the badge's firmware and gotten the strings, and people had figured out that you could pair badges together, but there wasn't much else.

### Starting the reverse engineering

The real work began on Friday. Someone had spun up a Slack channel and there was some discussion ongoing there. Someone uncovered the U7 flip trick. Another person with a PIC programmer (negative_alpha) had made some small discoveries which looked somewhat promising - I decided to meet up with him on Friday afternoon to get up to speed on what he'd uncovered, as well as get a disassembly from MPLAB X IDE of the badge firmware. He also dumped my friend's never-powered-on badge so that we could get a diff of that clean badge state with ours. We met up later again after dinner to work on the badge some more - he'd popped the hex in IDA and gotten something that didn't look like complete garbage. I decided to do the same and start my reverse engineering of the badge firmware.

Luckily, the code protection on the badge was disabled due to a bug with the PICKit 4. Unluckily, the debugger didn't work on the badge - a breakpoint could be set, but after the breakpoint was hit nothing would work. I later discovered that this was because the badge firmware wrote to parts of memory usually reserved for the debugger, probably on purpose. However, this was still a useful tool - we could at least look at all memory above 0x80000200 (everything below was reserved and not readable in MPLAB X IDE) as well as inspect the registers. It wasn't much, but it was something.

We quickly figured out that the badge pairing state was stored at 0x9d03f800 in flash. I used this knowledge and worked my way backwards in IDA, eventually uncovering the code that actually saved the state. He decided to zero out all the bytes at the relevant addresses, which funnily enough resulted in us actually not needing the v1 firmware patch later on (though we didn't know it at the time). I also uncovered the existence of a debug mode in the firmware, but we weren't sure how to access it.

### Forming the group

I met up with 0x01Atlas and company Saturday afternoon. He and his group had successfully reverse engineered the badge pairing protocol and used an Arduino to replay the pairing messages. I figured we should use whatever talent we had available to cooperatively solve the badge (I learned later that there was another group called the Crazy 8s that were "competing" with us? Would have been nice to know during the event, but oh well). I also wanted to pick 0x01Atlas's brain to see if there was any new information I could use in order to provide another foothold into reverse engineering the firmware. I'd made some progress, but hardly enough, so anything would have been useful.

Unfortunately, I didn't learn anything new, but we did manage to figure out how to turn the C green (by flashing the correct bytes with a programmer) and by extension also figured out how to turn the N green. The v0 pairing bug reared its head here when we tried pairing 2 green N badges, but we didn't even realize it was a bug since we'd flashed our firmwares and bypassed the bug entirely.

Zwiehunder dumped the PIC12F508 (U7) firmware Friday evening. I'd end up wasting several hours of my time analyzing 64 bytes of PIC assembly alongside a veteran PIC programmer. Neither of us could understand what the code was supposed to be doing - it seemed to just set some registers and then loop with no side effects. When wireng and friends swung by the Flamingo chill out room later that night, I got a harsh dose of reality: the PIC12 had code protection enabled so I'd effectively been analyzing garbage.

I continued grinding away at my disassembly while the other people in the room worked on their things. We hadn't made much progress by the end of the night. To the contrary, we learned that there was at least one other firmware bug that would prevent progress, meaning that cheating was now the only way to solve the badge.

### Cheating

Of course, if I was going to cheat at this puzzle, I was going to do it in style, aka make my cheat as minimal as possible. There had been a couple of other groups that had hardware modified their badges to cheat, but I wanted mine to be software only so absolutely no hardware modifications would be required.

By this point, it was well known that letter state was not persistent. This meant that the green/red status could not be faked by simply overwriting some nonvolatile memory - there was no way around code changes.

I spent all day Sunday just hacking away at the badge. By this point, I'd figured out at least how all the initialization occurred, how console printing worked, the purpose of a lot of the still barely annotated assembly code, and roughly where the puzzle check was happening. As expected, the puzzle check code was so highly obfuscated, I knew there was no way I would be able to understand how it worked before the closing ceremony. Patching the badge checks themselves was looking increasingly impractical.

With the clock ticking, there were few options remaining. I looked up the datasheet for the IS31FL3236 I2C LED controller and traced every code path that touched the I2C transmit/receive register addresses in any way. I'd decided to focus my efforts on writing some assembly code that would set all the LEDs green. wireng had mentioned on Saturday when I ran into him that there would be no other effect after all LEDs had been set green, so this sounded like the best approach for a minimal cheat.

Eventually, I found some code that seemed to do a memory copy in a loop that ran for 0x24 iterations. 0x24 in hex is 36, which is exactly the number of channels the LED controller had. Knowing this, the theory was that I could point the I2C write routine to some unused flash where we could dump our payload, but I had to confirm that this was a memory copy first - replacing one of the byte store instructions with a NOP seemed suitable. negative_alpha gladly acted as the guinea pig. I turned back to my laptop to start writing the green LED set code when suddenly...

"Dude, high five!"

I looked back, confused, then I saw negative_alpha's badge. All the letters and person LEDs were lit. Technically, the letters weren't green (they were yellow), but you'd never notice it at a glance - this was deemed "good enough" by the group and we quickly flashed our badges as it was almost 4pm. I let SamG0ld know that we'd "solved" the puzzle, and we hurried off to the closing ceremonies in the hopes of acquiring a black badge.

Sadly, the black badge was not to be. However, Tymkrs considered our cheat a win anyway, so there's that, I guess?

### Post-DEFCON

Everyone went back to their daily lives, mostly satisfied that the badge had been "solved". But I felt like the patch I'd accidentally discovered was just not good enough.

Work continued on the Slack. braz and Trevor Roach decided to look into the behavior of U7 since it was pretty well known by now that it acted as a LFSR. I bought a Saleae Logic Pro 16 and PICKit to run my own experiments with the LFSR. Now that we knew how to get into the debug menu, I was able to go full speed on continuing my reverse engineering work.

wireng posted a hardware AMA on reddit, and I took the opportunity to learn more about the LFSR behavior and the two remaining bugs. One seemed easy enough to fix (a bitflip), the other one not so much - it seemed like a high level architectural change more than anything. What made matters worse was that the architectural change was in the very large, annoyingly obfuscated puzzle check function. It made use of some tricks like using unaligned addresses for branches and jumps (MIPS ignores the least significant bit) which prevented autoanalysis, many overlapping memory reads/writes, and multiple levels of jump tables. I still have not figured out completely how this function works and as such had to wait for the v2 firmware to drop before the O could be solved.

In the meantime, I wrote a patcher to speed up the process of making changes to the firmware hex and to make patches portable across firmware versions. A lot of state was stored below 0x80000200, so I started working on a memory dump routine that would allow me to dump those 512 bytes using the debug menu (though I didn't get it working and soon stopped work on this). I started looking into the LFSR behavior of U7 while in 64-bit mode as well, accidentally managing to blow up my board by feeding 5v into the 3.3v rail and also taking out my computer's front USB ports and RAM in the process. (Thanks again to the kind redditors who offered their badges to me for free/cost of shipping!) I also traced the code paths that performed checks for the various hardware puzzles, using the debug menu to help guide my assumptions. Patching the code that checked the hall effect sensor was easy enough. Finding the code that checked for the blinking on the console was harder, especially since the code was bugged.

### Solving the green E

I spent a few days taking notes and mapping out every access to the I/O registers, plus reconstructing a barebones schematic using my fried badge as a reference. The reasoning here was that all hardware puzzles interacted with hardware external to the PIC32. So far we had had no idea how the code for puzzles 1 (blinking), 2 (Bobo's head) and 3 (U7 flip) worked, but now that we knew what all the hardware puzzles were supposed to be, I could trace accesses to the various port registers back to the code performing the checks.

A subroutine at 0x9d009034 in the v0 firmware jumped out as a result of this process. All it did was return a 3-bit-wide bitfield checking whether the blinking terminal was still blinking or not. I noticed that the result of this function seemed to be used incorrectly - the upper bit noting whether the result was valid or not was being XOR'd when it shouldn't have been. Once I realized this, the patch was just a simple bitflip in the firmware and then shorting the C11 capacitor to stop the timer circuit from oscillating. Green E down.

But I wasn't going to stop there. I wanted to make a patch that would solve this for me without having to perform a hardware modification, and now that I knew how the code worked, it was simple. The debug menu had an option that would let you force the LED into an on or off state, and this was checked by the puzzle 1 check code to determine if the puzzle was solved or not. By patching the puzzle 1 check code to force this bit to zero, that problem was gone. The other issue involved forcing the LED on without using the debug menu. Some careful assembly code optimization plus a few additions of my own to latch the appropriate pins high did the trick.

### Solving the green O

As mentioned before, I didn't think I'd be able to solve the green O. The code that determined the O's state was far too complex for me to understand at assembly language level. My work stalled here since I decided to work on other projects instead.

The v2 firmware eventually dropped, and Professor Plum was able to use my notes as well as some of the other previous discoveries to solve the green O. I'd already known that 0xFEEDB0B0DEADBEEF had to be fed least significant bit first to U4 by analyzing the debug menu's behavior when testing puzzle 2, and things were straightforward from there. He also uncovered the arcade room easter egg by just feeding the arcade poster hex string with a flipped U7.

And the rest, they say, is history.

## Credits

Thanks to the following people (in no particular order, let me know if I forgot your name)

* negative_alpha and Zwiehunder - brought a ton of useful gear and expertise to DC26, figured out pairing/karma states and U7's LFSR behavior
* braz and Trevor Roach - figured out how to bruteforce the LFSR in 8 bit mode
* Professor Plum - discovered how to legitimately solve Bobo's head (green O) in v2 firmware, also found the arcade room easter egg when U7 is flipped
* 0x01Atlas - reverse engineered the badgebus/pairing protocol and also made (one of) the badge emulators
* repentsinner - setting up the Slack channel where we could share information and coordinate groups to work on the badge
* SamG0ld - for being our test goon, helping to coordinate efforts and vouching for our group at DC26
* Several kind souls on reddit who donated their badges to me after I blew mine up

![green badge](https://i.imgur.com/aR6l4I5.jpg)