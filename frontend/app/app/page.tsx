"use client";

import ContactButton from "@/components/ContactButton";
import ProfileMenu from "@/components/ProfileMenu";
import {
  Grid,
  GridItem,
  Flex,
  Box,
  Button,
  CloseButton,
  Menu,
  Portal,
  Dialog,
} from "@chakra-ui/react";
import { CgFile, CgLogOut, CgUserAdd } from "react-icons/cg";

export default function App() {
  return (
    <Grid templateColumns="0.5fr 4fr" height="100vh">
      <GridItem borderWidth="2px" borderColor="gray.700" p="1px">
        <Flex
          direction="column"
          height="100%"
          borderRight="1px"
          borderColor="gray.500"
        >
          <ContactButton
            avatar="https://i.pravatar.cc/300"
            number={123123123}
            ID="XD"
          />
          <ContactButton
            avatar="https://i.pravatar.cc/300"
            number={123123123}
            ID="XD"
          />
          <ContactButton
            avatar="https://i.pravatar.cc/300"
            number={123123123}
            ID="XD"
          />
          <Box marginTop="auto">
            <Menu.Root>
              <Menu.Trigger asChild>
                <Button
                  height="fit-content"
                  bg="blue.400"
                  margin="0.5vh 0 0 0"
                  cursor="pointer"
                >
                  <ProfileMenu
                    avatar="https://i.pravatar.cc/300"
                    number={123123123}
                  />
                </Button>
              </Menu.Trigger>
              <Portal>
                <Menu.Positioner>
                  <Menu.Content>
                    <Menu.Item value="addContact">
                      <CgUserAdd />
                      <Box flex="1">Add contact</Box>
                    </Menu.Item>
                    <Menu.Item value="changeAvatar">
                      <CgFile />
                      <Box flex="1">Change avatar</Box>
                    </Menu.Item>
                    <Menu.Item
                      value="signOut"
                      color="fg.error"
                      _hover={{ bg: "bg.error", color: "fg.error" }}
                    >
                      <CgLogOut />
                      <Box flex="1">Sign out</Box>
                    </Menu.Item>
                  </Menu.Content>
                </Menu.Positioner>
              </Portal>
            </Menu.Root>
          </Box>
        </Flex>
      </GridItem>
      <GridItem>
        <p>Hey</p>
      </GridItem>
    </Grid>
  );
}
