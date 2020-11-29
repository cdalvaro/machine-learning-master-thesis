
import sys
sys.path.append('../')
from pycore.tikzeng import *

# defined your arch
arch = [
    to_head( '..' ),
    to_cor(),
    to_begin(),
    to_Conv("input", 4, '', offset="(0,0,0)", to="(0,0,0)", height=2, depth=2, width=2, caption='input' ),
    to_Conv("encoder_0", 50, '', offset="(2,0,0)", to="(input-east)", height=2, depth=10, width=2, caption='encoder\_0' ),
    to_connection( "input", "encoder_0"),
    to_Conv("encoder_1", 50, '', offset="(2,0,0)", to="(encoder_0-east)", height=2, depth=10, width=2, caption='encoder\_1' ),
    to_connection( "encoder_0", "encoder_1"),
    to_Conv("encoder_2", 200, '', offset="(2,0,0)", to="(encoder_1-east)", height=2, depth=20, width=2, caption='encoder\_2' ),
    to_connection( "encoder_1", "encoder_2"),
    to_Conv("encoder_3", 5, '', offset="(2,0,0)", to="(encoder_2-east)", height=2, depth=2, width=2, caption='encoder\_3' ),
    to_connection( "encoder_2", "encoder_3"),
    to_SoftMax("clustering", 5 ,"(2,0,0)", "(encoder_3-east)", height=2, depth=2, width=2, caption='clustering'  ),
    to_connection("encoder_3", "clustering"),
    to_Pool("output", offset="(2,0,0)", to="(clustering-east)", height=2, depth=2, width=2, caption='output' ),
    to_connection("clustering", "output"),
    to_end()
    ]

def main():
    namefile = str(sys.argv[0]).split('.')[0]
    to_generate(arch, namefile + '.tex' )

if __name__ == '__main__':
    main()
